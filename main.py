from fastAPI import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse


app = FastAPI()


class PersonalInfo(BaseModel):
    firstname: str
    lastname: str
    email: str
    fields: list[str]
    keywords: list[str]
    description: str
    main_skills: list[str]
    studies: str
    links: list[str]


class ProjectDescription(BaseModel):
    scope: str
    why: str
    context: str
    collaborators: list[str]
    url: str


class ProjectVisual(BaseModel):
    image: str
    video: str

class Eportfolio(BaseModel):
    personal_info : PersonalInfo
    project_description : list[ProjectDescription]
    projec_visual : list[ProjectVisual]

@app.get("/")
def home_page():
    return


@app.get("/eportfolio/{id}")
def get_portfolio(id:{id}):
    pass

@app.post("/eportfolio/create")
def create_portfolio(eportfolio: Eportfolio):
    return ""


