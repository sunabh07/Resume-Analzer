from pydantic import BaseModel,Field
from langchain_core.messages import BaseMessage
from typing import Optional, List, Annotated
from langgraph.graph.message import add_messages


class Repo(BaseModel):
    name: str
    url: Optional[str] = None
    description: Optional[str] = None
    stars: Optional[int] = 0
    forks: Optional[int] = 0
    languages: List[str] = []
    updated_at: Optional[str] = None
    readme_summary: Optional[str] = ""


class chat_schema(BaseModel):
    messages:Annotated[list[BaseMessage],add_messages]
    jd:Optional[str]=None
    filename:str
    resume_content:Optional[str]=None
    education_score:Optional[str]=None
    skills_score:Optional[str]=None
    github_repos:Optional[List[Repo]]=None
    projects_score:Optional[str]=None
