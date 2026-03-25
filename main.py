from fastAPI import FastAPI
from pydantic import BaseModel


app = FastAPI()


class PersonalInfo(BaseModel):
    firtsname : str
    lastname : str
    email : str
    fields : list[str]
    keywords : list[str]
    description : str
    main_skills : list[str]
    studies : str
    links : list[str]

class ProjectDescription(BaseModel):
    scope : str
    why : str
    context : str
    collaborators : list[str]
    url : str 

class ProjectVisual(BaseModel):
    
    
@app.get("/")
def home_page():
    return {"hello"}

