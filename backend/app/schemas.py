from typing import Literal
from pydantic import BaseModel, Field


class WorkItem(BaseModel):
    title: str
    project: str | None = None
    type: Literal["idea", "task", "note"] = "note"
    summary: str
    tasks: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    title: str
    project: str
    type: Literal["existing_project", "new_project", "idea", "task", "note"] = "idea"
    summary: str
    tasks: list[str] = Field(default_factory=list)


class PersonalItem(BaseModel):
    title: str
    type: Literal["reminder", "wishlist", "idea", "note"] = "note"
    summary: str


class CalendarEvent(BaseModel):
    title: str
    category: Literal["work", "private"] = "private"
    date: str
    start_time: str | None = None
    end_time: str | None = None
    all_day: bool = True
    notes: str | None = None


class AnalysisResult(BaseModel):
    summary: str
    work_items: list[WorkItem] = Field(default_factory=list)
    project_items: list[ProjectItem] = Field(default_factory=list)
    personal_items: list[PersonalItem] = Field(default_factory=list)
    calendar_events: list[CalendarEvent] = Field(default_factory=list)


ANALYSIS_JSON_SCHEMA = {
    "name": "voice_note_analysis",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "summary": {"type": "string"},
            "work_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "project": {"type": ["string", "null"]},
                        "type": {
                            "type": "string",
                            "enum": ["idea", "task", "note"]
                        },
                        "summary": {"type": "string"},
                        "tasks": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["title", "project", "type", "summary", "tasks"]
                }
            },
            "project_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "project": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": [
                                "existing_project",
                                "new_project",
                                "idea",
                                "task",
                                "note"
                            ]
                        },
                        "summary": {"type": "string"},
                        "tasks": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["title", "project", "type", "summary", "tasks"]
                }
            },
            "personal_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": ["reminder", "wishlist", "idea", "note"]
                        },
                        "summary": {"type": "string"}
                    },
                    "required": ["title", "type", "summary"]
                }
            },
            "calendar_events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "category": {
                            "type": "string",
                            "enum": ["work", "private"]
                        },
                        "date": {"type": "string"},
                        "start_time": {"type": ["string", "null"]},
                        "end_time": {"type": ["string", "null"]},
                        "all_day": {"type": "boolean"},
                        "notes": {"type": ["string", "null"]}
                    },
                    "required": [
                        "title",
                        "category",
                        "date",
                        "start_time",
                        "end_time",
                        "all_day",
                        "notes"
                    ]
                }
            }
        },
        "required": [
            "summary",
            "work_items",
            "project_items",
            "personal_items",
            "calendar_events"
        ]
    }
}