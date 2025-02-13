from fastapi import FastAPI, File, UploadFile, Form  # Import Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv
import json  # Import json

from services.file_processor import FileProcessor
from services.anki_generator import AnkiDeckInterface
from services.validator import Validator
from services.card_creator import LLMCardCreator
from config import Settings

load_dotenv()

app = FastAPI(title="Notes2Anki API")
settings = Settings()
validator = Validator(settings)
processor = FileProcessor(settings)

origins = ["http://localhost:3000"]

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model
class GenerateRequest(BaseModel):
    id: str
    anki_filename: str


# Response model
class GenerateResponse(BaseModel):
    id: str
    anki_file_url: str


@app.post("/generate", response_model=GenerateResponse)
async def generate_flashcards(
    request: str = Form(...),  # Expect 'request' as a form field
    files: List[UploadFile] = File(...),
):
    # Parse the JSON string from the form field into a dictionary
    request_data = json.loads(request)
    # Manually create a GenerateRequest object from the dictionary
    generate_request = GenerateRequest(**request_data)

    validator.validate_file_count(files)

    all_cards = {}
    for file in files:
        # Process files
        file_contents = processor.process_file(file)

        # Use LLM to create cards
        creator = LLMCardCreator()
        cards = creator.create_cards(file_contents)

        all_cards[file.filename] = cards

    # Generate Anki package
    generator = AnkiDeckInterface()
    anki_file_path = generator.generate_deck(
        all_cards,
        generate_request.anki_filename,
    )  # Use generate_request

    # TODO: do this properly
    # Generate download URL
    # download_url = f"{settings.BASE_URL}/downloads/{anki_file_path}"
    download_url = ""
    return GenerateResponse(
        id=generate_request.id, anki_file_url=download_url  # Use generate_request
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)