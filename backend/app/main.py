from fastapi import FastAPI,HTTPException,File,UploadFile,status,Depends,Body
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
import logging
from app.services.message import MessageService
from app.services.document import DocumentService
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)


app=FastAPI()
doc_service=DocumentService()
msg_service=MessageService()


# @app.post("/register",description="Registering a new user")
# async def register(email:EmailStr,password:str,full_name:str):
#     logger.info("Inside register function")
    
#     if not email:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="The Email parameter is required"
#         )
#     if not password:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="The password parameter is required"
#         )
#     if not full_name:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="The full_name parameter is required"
#         )
#     if len(password)<5:
#           raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="The length of password must be greater than 5"
#         )
    
#     result = await db_service.add_user(email,password,full_name)

#     return result

# @app.post("/login",description="Login in the user")
# async def login(email:EmailStr,password:str):
#     if not email:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="The Email parameter is required"
#         )
#     if not password:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="The password parameter is required"
#         )

#     user=await db_service.fetch_user(email,password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="The user is not found"
#         )
#     token_data={
#         "email":email,
#         "exp":datetime.utcnow()+timedelta(hours=1)
#         }
#     token=jwt.encode(token_data,os.getenv("JWT_SECRET"),algorithm="HS256")
#     return {
#     "message":"User logged in successfully",
#     "token":token
#     }

@app.post("/ask",description="Asking queries with the AI Regarding the Resume and JD")
async def ask_question(
    query:str=Body(...,embed=True),
    file:UploadFile=File(...)
):
    logger.info("Inside asking query function")
    if not file:
        raise HTTPException(
            status_code=401,
            detail="File is required in this field"
        )
    
    try:
        filename=await doc_service.save_file(file)
        logger.info("File saved to folder")
       
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Error occured during file upload: {e}"
        )
    
    content=await doc_service.fetch_content(filename)

    result=await msg_service.process_message(query,filename,content)

    if result["error"]:
        raise HTTPException(
            status_code=401,
            detail="Error occured during process message"
        )

    return {
        "answer":result["answer"]
    }

    

  
    



    

