from fastapi import HTTPException,UploadFile
import os
import tempfile
from pathlib import Path
from langchain_community.document_loaders import UnstructuredPDFLoader
import logging
import fitz  # PyMuPDF
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent # go to project root

FILE_DIR = BASE_DIR / "backend" / "files"

os.makedirs(FILE_DIR, exist_ok=True)

class DocumentService():
    async def save_file(self,file:UploadFile):

        filename=file.filename
        temp_path=os.path.join(tempfile.gettempdir(),filename)
        file_bytes=await file.read()
           

        with open(temp_path,"wb") as f:
            f.write(file_bytes)
        
        doc = fitz.open(temp_path)
        text_content = ""
        links = []
       
        for page in doc:
            text_content += page.get_text()

            for link in page.get_links():
                if "uri" in link:
                    links.append(link["uri"])
        unique_links = list(set(links))

        # Create formatted section
        links_section = "\n\n---\n\n### Extracted Links\n"
        for link in unique_links:
            links_section += f"- {link}\n"

        # Append to text_content
        text_content = text_content + links_section




        file_path=Path(FILE_DIR)/f"{filename}.md"
        with open(file_path,"w",encoding="utf-8") as f:
            f.write(text_content)
        logger.info("file saved")

        return filename
    
    async def fetch_content(self, filename: str):
        try:
            file_path = (FILE_DIR / f"{filename}.md").resolve()

            
            if file_path.parent != FILE_DIR:
                logger.error("File path outside allowed directory")
                return ""

            if not file_path.exists():
                logger.error(f"File does not exist: {file_path}")
                return ""

            if not file_path.is_file():
                logger.error(f"Not a file: {file_path}")
                return ""

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            logger.info(f"File read successfully: {filename}")

            return content

        except Exception as e:
            logger.error(f"Error in fetch_content: {str(e)}")
            return ""

            



