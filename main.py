from fastapi import Depends, FastAPI, Request, HTTPException, Form
from pydantic import BaseModel, EmailStr

# from fastapi.templating import Jinja2Templates
from typing import Annotated
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
from passlib.context import CryptContext
import uuid  # tokn de session

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# templates = Jinja2Templates(directory="Templates")

# nom du fichier de
sqlite_file_name = "test_database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

#
connect_args = {"check_same_thread": False}
# enginr détient les connexions à la base de données (il faut un seul object engine) afin de se connecter à la même base
engine = create_engine(sqlite_url, connect_args=connect_args)

pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto"
)  # hash de sessions pour mdp secure
sessions = {}


def create_db_and_tables():
    # Créer la base de données au démarage si elle n'existe pas
    SQLModel.metadata.create_all(engine)


# Permettre de stocker les objects en mémoire
def get_session():
    with Session(engine) as session:
        # Fournir une nouvelle sesion pour chaque requête
        yield session


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="Templates")

# Créer les tables de base de données au démarage de l'app (si elle n'existe pas)
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


SessionDep = Annotated[Session, Depends(get_session)]


########################################################################
# PArtie authentification et gestion des comptes
class AppUser(SQLModel, table=True):  # stockage des comptes crés sur le site
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    role: str = "user"


# conditions sur les mdp
def hash_password(password: str):
    return pwd_context.hash(password[:72])


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password[:72], hashed_password)


def get_current_user(request: Request, session: Session):  # identify user
    session_token = request.cookies.get("session_token")  #reuse the session token to avoid unecessary database lookup

    if not session_token or session_token not in sessions:
        return None

    user_id = sessions[session_token]
    return session.get(AppUser, user_id)


##################### gestion des accès et roles
def require_user(request: Request, session: SessionDep):
    user = get_current_user(request, session)

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return user


def require_admin(request: Request, session: SessionDep):
    user = require_user(request, session)

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    return user


#####################
class PersonalInfo_User(SQLModel):
    firstname: str
    lastname: str
    email: str
    fields: str
    keywords: str
    description: str
    main_skills: str
    studies: str
    links: str


class PersonalInfo_Session(PersonalInfo_User, table=True):
    user_id: int | None = Field(default=None, primary_key=True)


class ProjectDescription(SQLModel):
    scope: str
    why: str
    context: str
    collaborators: str
    url: str


class Project(ProjectDescription, table=True):
    project_id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="personalinfo_session.user_id")


class ProjectVisual(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    image: str
    video: str
    url: str
    comments: str | None = None
    project_id: int = Field(foreign_key="project.project_id")


class ProjectVisualInput(SQLModel):
    image: str
    video: str
    url: str
    comments: str | None = None


#############################################################################
class Eportfolio(BaseModel):
    personal_info: PersonalInfo_User
    project_description: list[ProjectDescription]
    project_visual: list[ProjectVisualInput]


# Mettre quelque part une response filtrer pour que l'utilisateur ne voit pas l'ID juste les infos qu'il doit entrer


@app.get("/")
def landing_page():
    return FileResponse("Templates/landing.html")


@app.get("/auth")
def auth_page():
    return FileResponse("Templates/auth.html")


@app.get("/portfolio")  # accès uniquement si connecté
def portfolio_page(request: Request, session: SessionDep):
    user = require_user(request, session)

    if user.role == "admin":
        return RedirectResponse("/admin", status_code=303)

    return FileResponse("Templates/index.html")


@app.get("/admin")
def admin_page(request: Request, session: SessionDep):
    require_admin(request, session)
    return FileResponse("Templates/admin.html")  # accès admin


@app.post("/register")
def register(
    session: SessionDep, email: EmailStr = Form(...), password: str = Form(...)
):
    existing_user = session.exec(select(AppUser).where(AppUser.email == email)).first()

    if existing_user:
        return HTMLResponse("Cet email est déjà utilisé.", status_code=400)

    user = AppUser(email=email, hashed_password=hash_password(password), role="user")

    session.add(user)
    session.commit()
    session.refresh(user)

    token = str(uuid.uuid4())
    sessions[token] = user.id

    response = RedirectResponse("/portfolio", status_code=303)
    response.set_cookie(key="session_token", value=token, httponly=True)

    return response


@app.post("/login")
def login(session: SessionDep, email: EmailStr = Form(...), password: str = Form(...)):
    user = session.exec(select(AppUser).where(AppUser.email == email)).first()

    if not user or not verify_password(password, user.hashed_password):
        return HTMLResponse("Email ou mot de passe incorrect.", status_code=401)

    token = str(uuid.uuid4())
    sessions[token] = user.id

    if user.role == "admin":
        redirect_url = "/admin"
    else:
        redirect_url = "/portfolio"

    response = RedirectResponse(redirect_url, status_code=303)
    response.set_cookie(key="session_token", value=token, httponly=True)

    return response


@app.get("/logout")  # déconnexion
def logout(request: Request):
    token = request.cookies.get("session_token")

    if token in sessions:
        del sessions[token]

    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("session_token")

    return response


# A modifier pour récupérer et envoyer les données à la DB
@app.post("/eportfolio")
def create_portfolio(eportfolio: Eportfolio, request: Request, session: SessionDep):

    current_user = require_user(request, session)
    user = PersonalInfo_Session(**eportfolio.personal_info.model_dump())

    session.add(user)  # add in database
    session.commit()
    session.refresh(user)

    for project_data in eportfolio.project_description:
        project = Project(**project_data.model_dump(), user_id=user.user_id)

        session.add(project)
        #session.commit()
        #session.refresh(project)
    session.commit()  # commit all projects at once to improve performance

    return {"message": "Portfolio créé avec succès", "user_id": user.user_id}

@app.get("/portfolio/{user_id}")
def show_portfolio(user_id: int, request: Request, session: SessionDep):
    user = session.get(PersonalInfo_Session, user_id)
    print(f"User trouvé : {user}")
    projects = session.exec(select(Project).where(Project.user_id == user_id)).all()
    skills   = [s.strip() for s in user.main_skills.split(",") if s.strip()] if user.main_skills else []
    keywords = [k.strip() for k in user.keywords.split(",") if k.strip()] if user.keywords else []
    return templates.TemplateResponse(
    request=request,
    name="portfolio.html",
    context={
        "personal": user,
        "projects": projects,
        "skills": skills,
        "keywords": keywords,
    })
# ???????????????????
# @app.post("/eportfolio/create")
# def create_portfolio(eportfolio: Eportfolio):
#     if not admin:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Not admin action",
#         )

#     return templates.TemplateResponse(
#         request,
#         "index.html",
#         context={"coffee": {}},
#     )


#     return ""
@app.get("/api/admin/users")  # sur admin permets d'afficher tous les comptes
def get_users(request: Request, session: SessionDep):
    require_admin(request, session)
    users = session.exec(select(AppUser)).all()
    return users


@app.post("/api/admin/users")  # créer un user
def create_user_admin(
    request: Request,
    session: SessionDep,
    email: EmailStr = Form(...),
    password: str = Form(...),
    role: str = Form(...),
):
    require_admin(request, session)

    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    existing_user = session.exec(select(AppUser).where(AppUser.email == email)).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = AppUser(email=email, hashed_password=hash_password(password), role=role)

    session.add(user)
    session.commit()

    return {"message": "Utilisateur créé"}


@app.post("/api/admin/users/{user_id}/role")  # modifier le role d'un user
def update_user_role(
    user_id: int, request: Request, session: SessionDep, role: str = Form(...)
):
    require_admin(request, session)

    user = session.get(AppUser, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    user.role = role
    session.add(user)
    session.commit()

    return {"message": "Rôle modifié"}


@app.delete("/api/admin/users/{user_id}")  # supprimer un user
def delete_user(user_id: int, request: Request, session: SessionDep):
    current_admin = require_admin(request, session)

    if current_admin.id == user_id:
        raise HTTPException(
            status_code=400, detail="Impossible de supprimer ton propre compte admin"
        )

    user = session.get(AppUser, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()

    return {"message": "Utilisateur supprimé"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
