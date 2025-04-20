from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List, Dict, BinaryIO
from pydantic import BaseModel
from dotenv import load_dotenv
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from services.file_processor import FileProcessor
from services.anki_generator import AnkiDeckInterface, ProcessedFileResult
from services.validator import Validator
from services.card_creator import Card, LLMCardCreator
from services.logger import app_logger, LoggerMixin
from services.exceptions import (
    ValidationError,
    FileValidationError,
    ProcessingError,
    LLMError,
    AnkiError,
    Notes2AnkiError,
)
from config import Settings
import time
import os
import zipfile
import csv
from datetime import datetime

load_dotenv()

app = FastAPI(title="Notes2Anki API")
settings = Settings()
validator = Validator(settings)
processor = FileProcessor(settings)
generator = AnkiDeckInterface()

origins = ["http://localhost:3000", "https://www.notes2anki.com"]

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email subscription model
class EmailSubscription(BaseModel):
    email: str

@app.post("/add_email")
async def subscribe_email(subscription: EmailSubscription):
    """Add an an email address to the mailing list"""
    try:
        # Create emails.csv if it doesn't exist
        if not os.path.exists("emails.csv"):
            with open("emails.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["email", "timestamp"])

        # Append the new email with timestamp
        with open("emails.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([subscription.email, datetime.now().isoformat()])

        return {"message": "Email subscribed successfully"}
    except Exception as e:
        app_logger.error(f"Error subscribing email: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to subscribe email")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors (e.g., missing required fields)"""
    app_logger.error(
        "Validation error",
        extra={
            "extra_fields": {
                "url": str(request.url),
                "method": request.method,
                "errors": exc.errors(),
            }
        },
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Notes2AnkiError)
async def notes2anki_error_handler(request: Request, exc: Notes2AnkiError):
    """Handle all Notes2Anki application errors"""
    # Map exception types to status codes
    status_codes = {
        ValidationError: 400,
        ProcessingError: 500,
        LLMError: 500,
        AnkiError: 500,
    }

    status_code = status_codes.get(type(exc), 500)

    app_logger.error(
        f"{type(exc).__name__} occurred",
        extra={
            "extra_fields": {
                "url": str(request.url),
                "method": request.method,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "details": getattr(exc, "details", None),
            }
        },
    )

    return JSONResponse(
        status_code=status_code,
        content={"detail": str(exc), "details": getattr(exc, "details", None)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle any unhandled exceptions"""
    app_logger.error(
        "Unhandled error",
        extra={
            "extra_fields": {
                "url": str(request.url),
                "method": request.method,
                "error": str(exc),
                # "error_type": type(exc).__name__,
            }
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please try again later."
        },
    )


@app.exception_handler(FileValidationError)
async def file_validation_exception_handler(request: Request, exc: FileValidationError):
    """Handle file validation errors (e.g., invalid file type)"""
    app_logger.error(
        "File validation error",
        extra={
            "extra_fields": {
                "url": str(request.url),
                "method": request.method,
                "error": str(exc),
                "details": exc.details,
            }
        },
    )
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    app_logger.info(
        "Request processed",
        extra={
            "extra_fields": {
                "method": request.method,
                "url": str(request.url),
                "client_host": request.client.host,
                "process_time_ms": round(process_time, 2),
                "status_code": response.status_code,
            }
        },
    )
    return response


# Request model
class GenerateRequest(BaseModel):
    id: str
    multiple_decks: bool = False
    output_format: str = "apkg"  # 'apkg', 'pdf', or 'csv'
    deck_names: Dict[str, str]  # mapping of filename to deck name


# Response model
class GenerateResponse(BaseModel):
    id: str
    files: List[Dict[str, str]]  # list of generated files with their paths


@app.post("/generate")
async def generate_flashcards(
    request: str = Form(...),
    files: List[UploadFile] = File(...),
):
    try:
        request_data = json.loads(request)
        generate_request = GenerateRequest(**request_data)
    except json.JSONDecodeError as e:
        raise RequestValidationError(
            [
                {
                    "loc": ["body", "request"],
                    "msg": "Invalid JSON",
                    "type": "json_decode_error",
                }
            ]
        )
    except Exception as e:
        raise RequestValidationError(
            [{"loc": ["body", "request"], "msg": str(e), "type": "validation_error"}]
        )

    app_logger.info(
        "Starting flashcard generation",
        extra={
            "extra_fields": {
                "request_id": generate_request.id,
                "multiple_decks": generate_request.multiple_decks,
                "output_format": generate_request.output_format,
                "file_count": len(files),
            }
        },
    )

    # All validation and processing errors are handled by exception handlers
    validator.validate_file_count(files)

    # Validate file extensions
    for file in files:
        validator.validate_file_ext(file)

    # Process all files concurrently using asyncio.gather
    results = await asyncio.gather(
        *[generator.process_single_file(file) for file in files]
    )

    output_files = []

    # FIXME: there is a bug where only the first deck gets images in it, why?
    if generate_request.multiple_decks:
        # Generate a deck for each file
        for res in results:
            # Reset the file pointer before processing each deck
            res.file.file.seek(0)
            
            deck_name = generate_request.deck_names.get(
                res.file.filename, res.file.filename.split(".")[0]
            )
            output_path = generator.generate_deck(
                processed_file_results=[
                    res
                ],  # Fix: Pass only the current file's result
                deck_name=deck_name,
                output_format=generate_request.output_format,
            )
            output_files.append(output_path)

        # Create a zip file containing all decks
        zip_path = os.path.join("./tmp", f"{generate_request.id}.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file_path in output_files:
                zipf.write(file_path, os.path.basename(file_path))
                # Clean up individual files after adding to zip
                os.remove(file_path)

        response_path = zip_path
    else:
        # Generate a single deck with all cards
        deck_name = generate_request.deck_names.get(
            files[0].filename, files[0].filename.split(".")[0]
        )
        response_path = generator.generate_deck(
            processed_file_results=results,
            deck_name=deck_name,
            output_format=generate_request.output_format,
        )

    app_logger.info(
        "Flashcard generation completed",
        extra={
            "extra_fields": {
                "request_id": generate_request.id,
                "total_files": len(files),
                # TODO: write logic to get total cards later
                # "total_cards": total_cards,
                "output_format": generate_request.output_format,
                "is_zip": generate_request.multiple_decks,
            }
        },
    )

    headers = {
        "X-Request-ID": generate_request.id,
        "Content-Disposition": f'attachment; filename="{os.path.basename(response_path)}"',
    }

    return FileResponse(
        response_path,
        headers=headers,
        media_type=(
            "application/zip"
            if generate_request.multiple_decks
            else f"application/{generate_request.output_format}"
        ),
    )


if __name__ == "__main__":
    import uvicorn

    app_logger.info("Starting Notes2Anki API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
