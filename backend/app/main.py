import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.config import get_settings
from app.services.obsidian_service import ObsidianService
from app.services.openai_service import OpenAIService
from app.services.project_service import load_project_index


settings = get_settings()
app = FastAPI(title="Voice Capture Backend")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/process-voice-note")
async def process_voice_note(
    file: UploadFile = File(...),
    recorded_at: str = Form(...),
    timezone: str = Form(default=settings.default_timezone),
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Dateiname fehlt.")

    try:
        datetime.fromisoformat(recorded_at)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="recorded_at muss ISO-Format haben, z. B. 2026-03-10T21:30:00+01:00",
        ) from exc

    uploads_dir = Path("data/uploads")
    transcripts_dir = Path("data/transcripts")
    analyses_dir = Path("data/analyses")

    uploads_dir.mkdir(parents=True, exist_ok=True)
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    analyses_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename).suffix or ".m4a"
    file_id = uuid4().hex
    stored_audio_path = uploads_dir / f"{file_id}{suffix}"

    content = await file.read()
    stored_audio_path.write_bytes(content)

    openai_service = OpenAIService(api_key=settings.openai_api_key)
    obsidian_service = ObsidianService(vault_path=settings.vault_path)

    transcript = openai_service.transcribe_audio(stored_audio_path)
    (transcripts_dir / f"{file_id}.txt").write_text(transcript, encoding="utf-8")

    project_index = load_project_index(settings.vault_path)

    analysis = openai_service.analyze_transcript(
        transcript=transcript,
        recorded_at=recorded_at,
        timezone=timezone,
        project_index=project_index,
    )

    (analyses_dir / f"{file_id}.json").write_text(
        analysis.model_dump_json(indent=2),
        encoding="utf-8",
    )

    obsidian_result = obsidian_service.write_analysis(
        result=analysis,
        transcript=transcript,
        recorded_at=recorded_at,
    )

    return {
        "ok": True,
        "transcript": transcript,
        "analysis": analysis.model_dump(),
        "obsidian": obsidian_result,
    }