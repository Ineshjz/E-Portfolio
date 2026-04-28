from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from typing import Annotated
from fastapi.responses import HTMLResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select

templates = Jinja2Templates(directory="Templates")

# nom du fichier de
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

#
connect_args = {"check_same_thread": False}
# enginr détient les connexions à la base de données (il faut un seul object engine) afin de se connecter à la même base
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    # Créer la base de données au démarage si elle n'existe pas
    SQLModel.metadata.create_all(engine)


# Permettre de stocker les objects en mémoire
def get_session():
    with Session(engine) as session:
        # Fournir une nouvelle sesion pour chaque requête
        yield session


app = FastAPI()


# Créer les tables de base de données au démarage de l'app (si elle n'existe pas)
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


SessionDep = Annotated[Session, Depends(get_session)]


########################################################################
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


class ProjectVisual(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    image: str
    video: str
    url: str
    comments: str | None = None
    project_id: int = Field(foreign_key="project.project_id")


#############################################################################
class Eportfolio(BaseModel):
    personal_info: PersonalInfo_User
    project_description: list[ProjectDescription]
    project_visual: list[ProjectVisual]


# Mettre quelque part une response filtrer pour que l'utilisateur ne voit pas l'ID juste les infos qu'il doit entrer


# ici doit contenir la première page que le navigateur doit afficher
@app.get("/")
def home_page(request: Request):
    return templates.TemplateResponse(request, "index.html")


# A modifier pour récupérer et envoyer les données à la DB
@app.post("/eportfolio")
def create_portfolio(eportfolio: Eportfolio):
    return eportfolio


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
