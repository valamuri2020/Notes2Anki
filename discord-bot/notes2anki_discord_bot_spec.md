# Notes2Anki Discord Bot - Feature Specification

**Bot Name**: `@notes2anki`  
**Purpose**: Interface with the existing Notes2Anki backend by allowing users to upload files directly from any Discord server.

---

## ✅ Functional Requirements

### 🧠 Bot Trigger Behavior
- **Trigger**: The bot listens for messages where it is mentioned (`@notes2anki`).
- **If the message does NOT include any file attachment**, it should respond with:
  > "Hey! Please attach a file for me to process – I can't help without one. 📎"

### 📎 Valid File Processing
- Users can upload **up to 5 files**, with a **maximum size of 15 MB per file**.
- Supported formats include `.pptx`, `.pdf`, `.docx`, `.md`, `.txt`, etc.
- Users can specify the desired output format in the message, e.g., `@notes2anki .apkg`. Supported outputs:
  - `.apkg`
  - `.pdf`
  - `.csv`
- If no format is specified, default to `.apkg`.

#### On valid file(s):
1. Bot replies:
   > "Got it! This may take a few minutes. ⏳"
2. Makes a request to the backend (`/generate`)
3. Awaits the response:
   - If one file, return `.apkg`, `.csv`, or `.pdf`
   - If multiple, returns a `.zip` file

4. Bot replies:
   > "Here’s your converted file! 🎉 *(Note: AI-generated cards may be imperfect – double-check before using!)*"

---

## ❌ Error Handling
- If backend fails or times out, bot replies with:
  > "Sorry, something went wrong. Please try again soon! ⚠️"

---

## 🔒 Rate Limiting
- Global backend rate limiting already exists.
- Add a soft **per-user cooldown** on the bot (e.g., **1 request every 30 seconds**) to prevent spam.

---

## 🧱 Tech Stack Recommendation

| Component           | Stack/Tool              |
|---------------------|-------------------------|
| Language            | Python                  |
| Framework           | discord.py              |
| HTTP Requests       | aiohttp                 |
| Secrets Management  | `.env` file             |

---

## 💡 Notes
- This is **only a frontend integration** with an already existing backend and product.
- Bot should support being added to **any Discord server** via OAuth2.
- Backend is located at: `https://api.notes2anki.com`

---

**Author**: [Vivek Alamuri]  
**Date**: April 13, 2025