## Resume Analyzer

An intelligent AI-powered Resume Analyzer built using FastAPI + LangGraph-style workflow orchestration that can:

Extract Job Descriptions (JD) from user input

Analyze resume data (skills, education, projects)

Answer resume-related questions

Dynamically route workflows using a graph-based system

------

## Features
Intelligent Chat Processing,
Detects whether user input is:

Job Description (JD)

Resume-related Question

Routes execution dynamically using conditional logic

------

## Workflow-Based Architecture
Built using StateGraph (LangGraph style) Modular node-based execution:

chat_node → intent detection

fetch_* → resume data extraction

question_node → Q&A handling

finalize → response generation

------
## Resume Data Processing
Extracts and processes:

👤 User details

🎓 Education

🛠 Skills

💼 Projects

------
## Question Answering System
Handles queries like:

Resume improvement tips

Skill suggestions

Interview preparation

------

## Architecture
<img width="1817" height="1203" alt="mermaid-diagram" src="https://github.com/user-attachments/assets/58dfef88-8096-410b-beb4-97f2fb33a21f" />

------

## Tech Stack

Backend: FastAPI

Workflow Engine: LangGraph / StateGraph

LLM Integration: OpenAI

Async Processing: Python Async/Await

Logging: Python Logging

-----

## Installation

1️ Clone the Repository

```
git clone https://github.com/sunabh07/Resume-Analzer.git

cd Resume-Analzer
```

2️ Create Virtual Environment

```
python -m venv venv

source venv/bin/activate   # Mac/Linux

venv\Scripts\activate      # Windows
```
3️ Install Dependencies
```
pip install -r requirements.txt
```

4️ Setup Environment Variables

Create a .env file:

```
OPENAI_API_KEY=your_api_key

GITHUB_PAT=your_github_token
```

5 Running the Application

```
uvicorn app.main:app --reload
```

-------

## Key Highlights

✔ Graph-based AI workflow orchestration

✔ Multi-intent query handling

✔ Modular and scalable backend design

✔ Async processing for efficiency

------

## License

This project is licensed under the MIT License.

------

## Contribute

Feel free to fork this repo and submit pull requests!

-------


## Support

If you like this project, give it a ⭐ on GitHub!
