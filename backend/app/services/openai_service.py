import json
from pathlib import Path
from openai import OpenAI

from app.schemas import ANALYSIS_JSON_SCHEMA, AnalysisResult


class OpenAIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def transcribe_audio(self, audio_path: Path) -> str:
        with audio_path.open("rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file,
            )

        return transcript.text.strip()

    def analyze_transcript(
        self,
        transcript: str,
        recorded_at: str,
        timezone: str,
        project_index: list[dict],
    ) -> AnalysisResult:
        system_prompt = """
Du analysierst Sprachmemos für ein persönliches Wissens- und Aufgabenmanagementsystem.

Deine Aufgaben:
1. Fasse das Memo kurz zusammen.
2. Trenne Inhalte in:
   - work_items
   - project_items
   - personal_items
   - calendar_events
3. Nutze bekannte Projekte aus project_index.
4. Wenn etwas klar zu einem bekannten Projekt gehört, nutze genau diesen Projektnamen.
5. Wenn ein neues Projekt erwähnt wird, trage es in project_items als new_project ein.
6. Erkenne Termine.
7. Relative Datumsangaben wie "morgen", "nächsten Montag", "übermorgen" müssen relativ zu recorded_at interpretiert werden.
8. Wenn keine Uhrzeit genannt wird, setze all_day = true und start_time/end_time = null.
9. Erfinde nichts. Wenn unsicher, lieber als Note statt als Kalendertermin.
10. Gib nur valides JSON zurück, passend zum Schema.
        """.strip()

        user_payload = {
            "recorded_at": recorded_at,
            "timezone": timezone,
            "project_index": project_index,
            "transcript": transcript,
        }

        response = self.client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(user_payload, ensure_ascii=False)
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": ANALYSIS_JSON_SCHEMA,
            },
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return AnalysisResult.model_validate(data)