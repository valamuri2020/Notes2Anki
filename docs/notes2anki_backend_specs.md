
# Notes2Anki.com Backend Specification

This document outlines the backend architecture, API structure, processing pipeline, and key considerations for **Notes2Anki.com**. The backend is responsible for handling file uploads, extracting text, generating Anki flashcards using an LLM, and serving the final `.anki` package to users.

---

## 1. Tech Stack
- **Framework:** FastAPI (Python) – for high-performance, async API handling.
- **File Parsing:** Doclings – for extracting structured text from various document formats.
- **LLM Integration:** Cohere API (initially, with model-agnostic design for future flexibility).
- **Storage:** Temporary in-memory storage or cloud storage for scalability.
- **Rate Limiting:** FastAPI middleware for request limiting.
- **Task Parallelization:** Async processing to handle multiple files concurrently.
- **Middleware-Ready Design:** Structure code to allow easy integration of authentication, observability, logging, and other middleware in the future.

---

## 2. API Design

### 2.1. Flashcard Generation Request
**Endpoint:** `POST /generate`

- **Description:** Accepts user files, processes text, generates Anki flashcards, and returns a downloadable `.anki` package.
- **Request Schema:**  
  ```json
  {
    "id": "req_12345",
    "num_cards": -1,  // Auto-detect number of cards, or specify up to 100
    "files": ["file1.pdf", "file2.pptx"]  // List of files uploaded
  }
  ```
- **Constraints:**  
  - **Max Files:** 5 per request  
  - **Max File Size:** 20MB per file  
  - **Allowed Types:** `PDF`, `PPTX`, `DOCX`, `TXT`  
- **Response Schema:**  
  ```json
  {
    "id": "req_12345",  // Corresponds to request ID
    "file": "https://Notes2anki.com/downloads/anki_12345.pkg"  // Download link
  }
  ```

---

## 3. Processing Pipeline

### 3.1. File Handling & Validation
- **Check file type & size** before processing.
- **Temporary storage:** Store files in memory or a temporary cloud bucket.
- **Parallel Processing:** Files are processed concurrently to improve speed.

### 3.2. Text Extraction & Processing
- **Use Doclings** for structured text extraction.
- **Sanitize text** (e.g., convert `amp; → &` and other HTML entities).
- **Optional Enhancements:**  
  - **Semantic Deduplication (LLM-based):**  
    ```text
    Perform text deduplication on this text. Return it in the same way with structure and markdown format intact but with deduplication applied.
    ```
  - **Removal of Extraneous Information (LLM-based):**  
    ```text
    Perform text deduplication and topic clustering on the following text. Remove extraneous information such as course-specific details (dates, times, locations, instructor names), image placeholders, repetitive slide headers, and purely presentational elements. Prioritize keeping content that would remain relevant across time. Return the processed text in the same structure and markdown format as the original.
    ```

### 3.3. LLM Processing
- **Each file is sent to Cohere’s API in parallel** to ensure citations at the file level.
- **Model-Agnostic Design:** API integration allows switching models later if needed.
- **Strict prompting & low temperature** to ensure accuracy and prevent hallucinations.
- **LLM Prompting Guidelines:**  
  - **Use only provided content** for flashcard generation.
  - **Maintain structure & citations per file.**

### 3.4. Flashcard Generation
- **Generate flashcards in structured JSON format.**
- **Convert JSON to `.anki` package** using `genanki`.
- **Store the `.anki` file temporarily** for download.

---

## 4. File Download Handling

### 4.1. How the Frontend Gets the File
- Backend **does not send the file directly** in the response (since files can be large).
- Instead, it provides a **download URL**:  
  ```json
  {
    "id": "req_12345",
    "file": "https://Notes2anki.com/downloads/anki_12345.pkg"
  }
  ```
- This URL allows the frontend to trigger a direct download.

### 4.2. Frontend Download Implementation
- When the user clicks the **download button**, the frontend initiates the file download using:  
  ```html
  <a href="https://Notes2anki.com/downloads/anki_12345.pkg" download>Download</a>
  ```

### 4.3. File Expiry & Cleanup
- Files **expire after 10 minutes** to save storage costs.
- If the user tries to download after expiration, they see an **expired link message**.

---

## 5. Middleware & Scalability Considerations

The backend is designed in a modular way, allowing easy integration of **middleware** such as:

### 5.1. Rate Limiting
- **Limit:** 10 requests per minute per IP
- Implemented via FastAPI’s dependency injection system.

### 5.2. Authentication (Future)
- While the MVP is fully anonymous, the backend will be structured to easily add **OAuth, API keys, or JWT authentication** later.

### 5.3. Observability & Logging
- Integrate **structured logging** (e.g., `loguru` or `structlog`) to track request flow.
- Add **Prometheus/Grafana** for monitoring key metrics (request volume, processing time, errors).

### 5.4. Error Handling
- Standardized **error responses** for predictable frontend handling:  
  ```json
  {
    "error": "File size exceeds limit",
    "code": 413
  }
  ```

---

## 6. Future Enhancements
- **AnkiWeb Integration:** Allow users to preview & edit decks in the browser before downloading.
- **Image Support:** Extract diagrams and figures for image-based flashcards.
- **Multi-Model Support:** Easily switch between LLM providers.
- **WebSocket Support:** For real-time progress updates instead of polling.

---

This document fully covers the backend's architecture while keeping it **scalable and middleware-ready**. 🚀
