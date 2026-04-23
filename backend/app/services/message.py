from app.graph.workflow import Workflow


from langchain.messages import AIMessage,HumanMessage
from app.graph.base import llm
import logging


logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)


work=Workflow()


class MessageService:
    async def process_message(self,query:str,filename:str,content:str):

        
        logger.info("Inside message workflow")
        app = await work.build_workflow()

        if not query:
            return {
                "error":"Empty message not allowed",
                "answer":None
                    }
          
        try:

            response=await app.ainvoke(
                {
                    "messages":[HumanMessage(content=query)],
                    "filename":filename,
                    "resume_content":content
                    
                }
            )
            ai_content=response['messages'][-1].content

            return {
                "answer":ai_content,
                "error":None
            }
        except Exception as e:
            logger.error(f"Error occured during chat,{str(e)}")
            return {
                "error":str(e),
                "answer":None
            }



      