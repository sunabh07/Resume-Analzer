from app.graph.base import llm
from langchain.messages import AIMessage, HumanMessage
from app.graph.schema import chat_schema
from langgraph.graph import StateGraph, START, END
from app.services.document import DocumentService
from app.services.github_services import GithubService
import httpx
import json
import asyncio
import logging
import re
import time
import os
from dotenv import load_dotenv
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 
# ---------------- LOGGING CONFIG ---------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

github_service=GithubService()
doc_service = DocumentService()


class Workflow():

    async def build_workflow(self):
        logger.info("Inside Build Workflow function")

        graph = StateGraph(chat_schema)

        # Nodes
        graph.add_node("chat_node", self.chat_node)
        graph.add_node("fetch_user", self.fetch_user)
        graph.add_node("fetch_education", self.fetch_education)
        graph.add_node("fetch_skills", self.fetch_skills)
        graph.add_node("fetch_projects", self.fetch_projects)
        graph.add_node("dummy_node", lambda state: state)
        graph.add_node("question_node", self.question_node) # Placeholder for question handling logic

        graph.add_node("finalize", self.finalize)

        # Start
        graph.add_edge(START, "chat_node")

        # Merge
        def route_from_chat(state: chat_schema):
            if state.question:
                return "question_node"
            else:
                return "dummy_node"
        
        graph.add_conditional_edges("chat_node",route_from_chat)

        graph.add_edge("dummy_node", "fetch_education")
        graph.add_edge("dummy_node", "fetch_skills")
        graph.add_edge("dummy_node", "fetch_projects")
        graph.add_edge("dummy_node", "fetch_user")

        graph.add_edge("fetch_user", "finalize")
        graph.add_edge("fetch_education", "finalize")
        graph.add_edge("fetch_projects", "finalize")
        graph.add_edge("fetch_skills", "finalize")

        graph.add_edge("question_node", END) 
        graph.add_edge("finalize", END)


        logger.info("Workflow compiled successfully")

        app=graph.compile()
 
        return app

        
# ----------- With JD nodes ------------ #
    
    async def chat_node(self, state: chat_schema):
        logger.info("Entered chat_node")

        try:
            message = state.messages
            logger.info(f"User message: {message}")

            prompt = f"""
        You are a Resume analyzer assistant.

Extract ONLY the Job Description (JD) from the user message.

If you think user wants to ask questions regarding resume building or wants to ask any question related to 
resume then you will not extract any JD and you will simply answer the question asked by the user and you
will not say anything about JD in that case.
and you will respond like 

"QUESTION": and then the actual question asked by the user without any extra text.

User Message: {message}

"""

            response = await llm.ainvoke(prompt)
            if "QUESTION" in response.content:
                question = response.content.split("QUESTION:")[1].strip()
                logger.info(f"Extracted question: {question}")
                return {"question": question, "jd": ""}
            else:

                jd = response.content.strip()

                logger.info(f"JD Extracted: {jd}")

                return {"jd": jd,"question": None}

        except Exception as e:
            logger.error(f"Error in chat_node: {str(e)}")
            return {"jd": "", "question": None}


    
    async def fetch_user(self, state: chat_schema):
        logger.info("Entered fetch_user")

        try:
           

            resume_content = state.resume_content

            if not resume_content:
                logger.error("Resume content is empty")
                return {"github_repos": []}

    
            github_links = github_service.extract_github_links(resume_content)


            logger.info(f"Extracted GitHub links: {github_links}")

            if not github_links:
                logger.warning("No GitHub links found in resume")
                return {"github_repos": []}

            repos_data = await github_service.fetch_all_github_data(github_links)

            logger.info(f"Total repos fetched: {len(repos_data)}")
        
            return {"github_repos": repos_data}

        except Exception as e:
            logger.error(f"Error in fetch_user: {str(e)}")
            return {"github_repos": []}
      
    async def fetch_skills(self, state: chat_schema):
        logger.info("Entered fetch_skills")

        try:
            resume_content = state.resume_content
            jd = state.jd

            logger.info(f"JD: {jd}")

            prompt = f"""
        You are an assistant whose task is to analyze skills score out of 10 for a given Job Descripiton (JD)
        You will be provided resume content and the JD and your task will be to evaluate the skills that the 
        person has which are relevant to the JD provided. Match Keywords in the JD and check whether the person has those skills or not.
        resume_content:{resume_content}
        jd:{jd}
        You dont have to hallucinate and only provide score out of 10.
        You must be precise in providing the score.
        Your output must be a number in string format score can be float,double, integer based on your evaluation
        Your output must be a number nothing else.

"""

            response = await llm.ainvoke(prompt)

            logger.info(f"Skills score: {response.content}")

            return {"skills_score": response.content}

        except Exception as e:
            logger.error(f"Error in fetch_skills: {str(e)}")
            return {"skills_score": "0"}

   
    async def fetch_education(self, state: chat_schema):
        logger.info("Entered fetch_education")

        try:
            resume_content = state.resume_content
            jd = state.jd

            prompt = f"""
        You are an assistant whose task is to analyze Education score out of 10 for a given resume
        You will be provided resume content and Job Description (JD)
        Your task will be to evaluate the education that a 
        person has, if a person is fresher then check the college, school, person's marks, CGPA, percentage
        If a person has done some degree from a government college, or a college with good reputation with good cgpa
        score good.
        If a certain amount of education is necessary in a certain JD then you have to give score according to it
        resume_content:{resume_content}
        JD:{jd}
        You dont have to hallucinate and only provide score out of 10.
        You must be precise in providing the score.
        Your output must be a number in string format score can be float,double, integer based on your evaluation
        Your output must be a number nothing else.

"""

            response = await llm.ainvoke(prompt)

            logger.info(f"Education score: {response.content}")

            return {"education_score": response.content}

        except Exception as e:
            logger.error(f"Error in fetch_education: {str(e)}")
            return {"education_score": "0"}

   
    async def fetch_projects(self, state: chat_schema):
        logger.info("Entered fetch_projects")

        try:
            resume_content = state.resume_content
            jd = state.jd

            prompt = f"""
        You are an assistant whose task is to analyze Projects score out of 10 for a given Job Descripiton (JD)
        You will be provided resume content and the JD and your task will be to evaluate the projects made by the
        user. 
        You will check all the projects made by the user what the user has done and what it has tried to implement
        skills that a user used to build, and difficulty or if a project is difficult and how does the resume speak of the project 
        you have to keep in notice.
        You will have to also check the JD and see whether these type of projects are needed or whether the technical or soft skills
        used to develop the project is useful in the JD. Skills used in the projects should match or should mean similar to the JD.
        You have to score the project based on these criteria
        resume_content:{resume_content}
        jd:{jd}
        You dont have to hallucinate and only provide score out of 10.
        You must be precise in providing the score.
        Your output must be a number in string format score can be float,double, integer based on your evaluation
        Your output must be a number nothing else.

"""

            response = await llm.ainvoke(prompt)

            logger.info(f"Projects score: {response.content}")

            return {"projects_score": response.content}

        except Exception as e:
            logger.error(f"Error in fetch_projects: {str(e)}")
            return {"projects_score": "0"}


    async def finalize(self, state: chat_schema):

        resume_content=state.resume_content
        jd=state.jd
        education_score=state.education_score
        skills_score=state.skills_score
        github_repos=state.github_repos
        projects_score=state.projects_score

        prompt=f"""
        You are an helpful agent whose task is to find wether the resume is suitable for the Job Description or not
        You are being provided with the resume content, JD, education score, skills score, github repos, projects score
        your task is to analyze all the fields and check wether the person is suitable for this role or not 
        You have to give suggestions also if you think the resume can be improved like skills projects or any certifications
        Give suggestions for some skills or keywords which the person can add in the resume to make it more suitable for the JD provided.
        You have to give suggestions based on the JD provided and the content of the resume provided.
        resume_content : {resume_content}
        jd:{jd}
        education_score:{education_score}
        skills_score:{skills_score}
        github_repos:{github_repos}
        projects_score:{projects_score}
  
        your output should contain the description of the profile stating whether the person is suitable or not and why
        and the output should contain the score of the profile on the scale of 10
        output should be a valid json without any extra symbols it should be like the example given with no extra symbols or characters
Return STRICTLY valid JSON in this exact format:

{{
    "Description": "<your analysis>",
    "Score": "<score>/10"
}}

Rules:
- Do NOT add any extra text before or after JSON
- Do NOT use markdown (no ```json)
- Do NOT escape quotes
- Ensure valid JSON (parsable by json.loads)


"""
        response=await llm.ainvoke(prompt)
        logger.info(f"This the response we got {response.content}")
        

        return {"messages":[AIMessage(content=response.content.strip())]}
    

    async def question_node(self, state: chat_schema):
        question=state.question
        logger.info(f"Handling question: {question}")
        resume_content=state.resume_content
        prompt=f"""
        You are an helpful assistant you will be given a question by the user regarding resume or anything or it can be related to 
        imporve his or her skills or whether questions regarding skills or interview questions. you have to respond according to that
        Question: {question}
        Resume content: {resume_content}

"""
        response=await llm.ainvoke(prompt)
        logger.info(f"Response to question: {response.content}")
        return {"messages":[AIMessage(content=response.content.strip())]}
