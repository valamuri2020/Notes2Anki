from fastapi import FastAPI, File, UploadFile, Form  # Import Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv
import json
from services.file_processor import FileProcessor
from services.anki_generator import AnkiDeckInterface
from services.validator import Validator
from services.card_creator import LLMCardCreator
from config import Settings
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

app = FastAPI(title="Notes2Anki API")
settings = Settings()
validator = Validator(settings)
processor = FileProcessor(settings)

origins = ["http://localhost:3000", "https://www.notes2anki.com"]
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


@app.post("/generate")
async def generate_flashcards(
    request: str = Form(...),
    files: List[UploadFile] = File(...),
):
    request_data = json.loads(request)
    generate_request = GenerateRequest(**request_data)

    validator.validate_file_count(files)

    all_cards = {}

    def process_single_file(file):
        file_contents = processor.process_file(file)
        creator = LLMCardCreator()
        cards = creator.create_cards(file_contents)
        return file.filename, cards

    with ThreadPoolExecutor() as executor:
        # Process files in parallel
        future_results = [executor.submit(process_single_file, file) for file in files]
        # Collect results
        for future in future_results:
            filename, cards = future.result()
            all_cards[filename] = cards

    generator = AnkiDeckInterface()

    anki_file_path = generator.generate_deck(
        all_cards,
        generate_request.anki_filename,
    )

    headers = {"X-Request-ID": generate_request.id}

    return FileResponse(
        path=anki_file_path,
        filename=generate_request.anki_filename,
        media_type="application/apkg",
        headers=headers,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
