from fastapi import Depends, FastAPI, Request, HTTPException, Form
from pydantic import EmailStr
from typing import Annotated
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
from passlib.context import CryptContext
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from enum import Enum
import uuid
import re
import os
from dotenv import load_dotenv

load_dotenv()

# ── BDD ───────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True,
    pool_recycle=300,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

# ── AUTH UTILS ────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password[:72])


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password[:72], hashed_password)


# ── SLUG UTILS ────────────────────────────────────────────────────────
def generate_slug(firstname: str, lastname: str, session: Session) -> str:
    base = f"{firstname}-{lastname}".lower()
    base = re.sub(r"[^a-z0-9-]", "", base.replace(" ", "-"))
    slug = base
    counter = 1
    while session.exec(select(Portfolio).where(Portfolio.slug == slug)).first():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


# ── MODELS ────────────────────────────────────────────────────────────
class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class AppUser(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    role: UserRole = UserRole.user
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserSession(SQLModel, table=True):
    token: str = Field(primary_key=True)
    user_id: int = Field(foreign_key="appuser.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Portfolio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="appuser.id")
    slug: str = Field(unique=True, index=True)
    is_public: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PersonalInfo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolio.id", unique=True)
    firstname: str
    lastname: str
    email: str
    fields: str = ""
    keywords: str = ""
    description: str = ""
    main_skills: str = ""
    studies: str = ""
    links: str = ""


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolio.id")
    scope: str
    why: str
    context: str
    collaborators: str
    url: str
    order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectVisual(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    image_url: str = ""
    video_url: str = ""
    project_url: str = ""
    comments: str | None = None


# ── SCHEMAS API ───────────────────────────────────────────────────────
class PersonalInfoInput(SQLModel):
    firstname: str
    lastname: str
    email: str
    fields: str = ""
    keywords: str = ""
    description: str = ""
    main_skills: str = ""
    studies: str = ""
    links: str = ""


class PersonalInfoResponse(SQLModel):
    portfolio_id: int
    slug: str
    firstname: str
    lastname: str
    fields: str
    main_skills: str


class ProjectInput(SQLModel):
    scope: str
    why: str
    context: str
    collaborators: str
    url: str


class ProjectVisualInput(SQLModel):
    image_url: str = ""
    video_url: str = ""
    project_url: str = ""
    comments: str | None = None


class EportfolioInput(SQLModel):
    personal_info: PersonalInfoInput
    project_description: list[ProjectInput]
    project_visual: list[ProjectVisualInput] = []


# ── SESSION HELPERS ───────────────────────────────────────────────────
def get_current_user(request: Request, session: Session):
    token = request.cookies.get("session_token")
    if not token:
        return None
    user_session = session.get(UserSession, token)
    if not user_session:
        return None
    return session.get(AppUser, user_session.user_id)


def require_user(request: Request, session: SessionDep):
    user = get_current_user(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_admin(request: Request, session: SessionDep):
    user = require_user(request, session)
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user


# ── APP ───────────────────────────────────────────────────────────────
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="Templates")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# ── PAGES ─────────────────────────────────────────────────────────────
@app.get("/")
def index_page():
    return FileResponse("Templates/index.html")


@app.get("/auth")
def auth_page():
    return FileResponse("Templates/auth.html")


@app.get("/dashboard")
def dashboard_page(request: Request, session: SessionDep):
    user = require_user(request, session)
    if user.role == UserRole.admin:
        return RedirectResponse("/admin", status_code=303)
    return FileResponse("Templates/dashboard.html")


@app.get("/generator")
def generator_page(request: Request, session: SessionDep):
    require_user(request, session)
    return FileResponse("Templates/parametrage.html")


@app.get("/admin")
def admin_page(request: Request, session: SessionDep):
    require_admin(request, session)
    return FileResponse("Templates/admin.html")


# ── AUTH ROUTES ───────────────────────────────────────────────────────
@app.post("/register")
def register(
    session: SessionDep, email: EmailStr = Form(...), password: str = Form(...)
):
    if session.exec(select(AppUser).where(AppUser.email == email)).first():
        return HTMLResponse("Cet email est déjà utilisé.", status_code=400)

    user = AppUser(email=email, hashed_password=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)

    token = str(uuid.uuid4())
    session.add(UserSession(token=token, user_id=user.id))
    session.commit()

    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(key="session_token", value=token, httponly=True)
    return response


@app.post("/login")
def login(session: SessionDep, email: EmailStr = Form(...), password: str = Form(...)):
    user = session.exec(select(AppUser).where(AppUser.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse("/auth?error=invalid", status_code=303)

    token = str(uuid.uuid4())
    session.add(UserSession(token=token, user_id=user.id))
    session.commit()

    redirect_url = "/admin" if user.role == UserRole.admin else "/dashboard"
    response = RedirectResponse(redirect_url, status_code=303)
    response.set_cookie(key="session_token", value=token, httponly=True)
    return response


@app.get("/logout")
def logout(request: Request, session: SessionDep):
    token = request.cookies.get("session_token")
    if token:
        user_session = session.get(UserSession, token)
        if user_session:
            session.delete(user_session)
            session.commit()
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("session_token")
    return response


# ── PORTFOLIO ROUTES ──────────────────────────────────────────────────
@app.post("/eportfolio")
def create_portfolio(
    eportfolio: EportfolioInput, request: Request, session: SessionDep
):
    current_user = require_user(request, session)

    slug = generate_slug(
        eportfolio.personal_info.firstname, eportfolio.personal_info.lastname, session
    )

    portfolio = Portfolio(user_id=current_user.id, slug=slug)
    session.add(portfolio)
    session.commit()
    session.refresh(portfolio)

    profile = PersonalInfo(
        **eportfolio.personal_info.model_dump(), portfolio_id=portfolio.id
    )
    session.add(profile)

    for project_data in eportfolio.project_description:
        project = Project(**project_data.model_dump(), portfolio_id=portfolio.id)
        session.add(project)

    session.commit()
    return {"message": "Portfolio créé avec succès", "slug": slug}


@app.get("/portfolio/{slug}")
def show_portfolio(slug: str, request: Request, session: SessionDep):
    portfolio = session.exec(select(Portfolio).where(Portfolio.slug == slug)).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio introuvable")

    profile = session.exec(
        select(PersonalInfo).where(PersonalInfo.portfolio_id == portfolio.id)
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil introuvable")

    projects = session.exec(
        select(Project).where(Project.portfolio_id == portfolio.id)
    ).all()

    skills = [s.strip() for s in profile.main_skills.split(",") if s.strip()]
    keywords = [k.strip() for k in profile.keywords.split(",") if k.strip()]

    return templates.TemplateResponse(
        request=request,
        name="portfolio.html",
        context={
            "personal": profile,
            "projects": projects,
            "skills": skills,
            "keywords": keywords,
        },
    )


@app.get("/portfolio")
def portfolio_redirect():
    return RedirectResponse("/dashboard", status_code=301)


# ── API ROUTES ────────────────────────────────────────────────────────
@app.get("/api/me")
def get_me(request: Request, session: SessionDep):
    user = get_current_user(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"email": user.email, "role": user.role, "id": user.id}


@app.get("/api/my-portfolios", response_model=list[PersonalInfoResponse])
def get_my_portfolios(request: Request, session: SessionDep):
    user = require_user(request, session)
    portfolios = session.exec(
        select(Portfolio).where(Portfolio.user_id == user.id)
    ).all()
    if not portfolios:
        return []

    result = []
    for p in portfolios:
        profile = session.exec(
            select(PersonalInfo).where(PersonalInfo.portfolio_id == p.id)
        ).first()
        if profile:
            result.append(
                PersonalInfoResponse(
                    portfolio_id=p.id,
                    slug=p.slug,
                    firstname=profile.firstname,
                    lastname=profile.lastname,
                    fields=profile.fields,
                    main_skills=profile.main_skills,
                )
            )
    return result


@app.get("/api/admin/users")
def get_users(request: Request, session: SessionDep):
    require_admin(request, session)
    return session.exec(select(AppUser)).all()


@app.post("/api/admin/users")
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
    if session.exec(select(AppUser).where(AppUser.email == email)).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    session.add(
        AppUser(email=email, hashed_password=hash_password(password), role=role)
    )
    session.commit()
    return {"message": "Utilisateur créé"}


@app.post("/api/admin/users/{user_id}/role")
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


@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, request: Request, session: SessionDep):
    admin = require_admin(request, session)
    if admin.id == user_id:
        raise HTTPException(
            status_code=400, detail="Impossible de supprimer ton propre compte"
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
