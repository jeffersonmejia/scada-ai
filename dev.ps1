$ErrorActionPreference = "Stop"

& ".\.venv\Scripts\python.exe" -m uvicorn main:app `
  --host 127.0.0.1 `
  --port 8000 `
  --reload `
  --reload-dir "C:\Users\ESPE-SD\Downloads\backend-llm"

