from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()
llm=ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# response=llm.invoke("Who is sachin tendulkar")
# print(response.content)