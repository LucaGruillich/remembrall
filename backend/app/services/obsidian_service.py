from datetime import datetime
from pathlib import Path

from app.schemas import AnalysisResult


class ObsidianService:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)

    def _ensure_dir(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def _append_markdown(self, file_path: Path, content: str) -> None:
        self._ensure_dir(file_path.parent)
        with file_path.open("a", encoding="utf-8") as f:
            f.write(content)
            if not content.endswith("\n"):
                f.write("\n")

    def _write_if_missing(self, file_path: Path, content: str) -> None:
        self._ensure_dir(file_path.parent)
        if not file_path.exists():
            with file_path.open("w", encoding="utf-8") as f:
                f.write(content)

    def _slug_safe(self, name: str) -> str:
        forbidden = '<>:"/\\|?*'
        cleaned = "".join("_" if ch in forbidden else ch for ch in name).strip()
        return cleaned or "Unbenanntes Projekt"

    def ensure_project_structure(self, project_name: str) -> Path:
        safe_name = self._slug_safe(project_name)
        project_dir = self.vault_path / "Projects" / safe_name
        self._ensure_dir(project_dir)

        self._write_if_missing(
            project_dir / "Overview.md",
            f"# {project_name}\n\n## Überblick\n\n"
        )
        self._write_if_missing(
            project_dir / "Ideas.md",
            f"# Ideen – {project_name}\n\n"
        )
        self._write_if_missing(
            project_dir / "Tasks.md",
            f"# Aufgaben – {project_name}\n\n"
        )
        self._write_if_missing(
            project_dir / "Notes.md",
            f"# Notizen – {project_name}\n\n"
        )

        return project_dir

    def write_analysis(
        self,
        result: AnalysisResult,
        transcript: str,
        recorded_at: str,
    ) -> dict:
        today = datetime.fromisoformat(recorded_at).date().isoformat()

        written_files: list[str] = []

        inbox_log = self.vault_path / "Inbox" / "Voice Notes"
        self._ensure_dir(inbox_log)

        transcript_file = inbox_log / f"{today}.md"
        self._append_markdown(
            transcript_file,
            (
                f"\n## Sprachmemo {recorded_at}\n\n"
                f"### Zusammenfassung\n{result.summary}\n\n"
                f"### Transkript\n{transcript}\n"
            ),
        )
        written_files.append(str(transcript_file))

        for item in result.work_items:
            if item.project:
                file_path = self.vault_path / "Work" / "Projects" / self._slug_safe(item.project) / "Notes.md"
                self._append_markdown(
                    file_path,
                    (
                        f"\n## {item.title}\n\n"
                        f"**Typ:** {item.type}\n\n"
                        f"{item.summary}\n\n"
                        + (
                            "### Aufgaben\n" +
                            "\n".join(f"- {task}" for task in item.tasks) +
                            "\n"
                            if item.tasks else ""
                        )
                    ),
                )
                written_files.append(str(file_path))
            else:
                file_path = self.vault_path / "Work" / "Inbox" / f"{today}.md"
                self._append_markdown(
                    file_path,
                    f"\n## {item.title}\n\n{item.summary}\n",
                )
                written_files.append(str(file_path))

        for item in result.project_items:
            self.ensure_project_structure(item.project)

            notes_file = self.vault_path / "Projects" / self._slug_safe(item.project) / "Notes.md"
            ideas_file = self.vault_path / "Projects" / self._slug_safe(item.project) / "Ideas.md"
            tasks_file = self.vault_path / "Projects" / self._slug_safe(item.project) / "Tasks.md"

            self._append_markdown(
                notes_file,
                f"\n## {item.title}\n\n{item.summary}\n",
            )
            written_files.append(str(notes_file))

            if item.type in {"new_project", "idea"}:
                self._append_markdown(
                    ideas_file,
                    f"\n## {item.title}\n\n{item.summary}\n",
                )
                written_files.append(str(ideas_file))

            if item.tasks:
                self._append_markdown(
                    tasks_file,
                    (
                        f"\n## {item.title}\n\n" +
                        "\n".join(f"- [ ] {task}" for task in item.tasks) +
                        "\n"
                    ),
                )
                written_files.append(str(tasks_file))

        for item in result.personal_items:
            if item.type == "wishlist":
                file_path = self.vault_path / "Personal" / "Wishlist" / f"{today}.md"
            elif item.type == "reminder":
                file_path = self.vault_path / "Personal" / "Reminders" / f"{today}.md"
            elif item.type == "idea":
                file_path = self.vault_path / "Personal" / "Ideas" / f"{today}.md"
            else:
                file_path = self.vault_path / "Personal" / "Inbox" / f"{today}.md"

            self._append_markdown(
                file_path,
                f"\n## {item.title}\n\n{item.summary}\n",
            )
            written_files.append(str(file_path))

        return {
            "written_files": sorted(set(written_files)),
        }