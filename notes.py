"""Простой консольный блокнот с JSON-хранилищем."""

import argparse
import json
from pathlib import Path


def load_notes(file_path: Path) -> list[dict]:
    if not file_path.exists():
        return []

    try:
        notes = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Файл {file_path} содержит некорректный JSON.") from error

    if not isinstance(notes, list):
        raise ValueError("Хранилище должно содержать JSON-массив заметок.")

    for note in notes:
        if (
            not isinstance(note, dict)
            or type(note.get("id")) is not int
            or note["id"] < 1
            or not isinstance(note.get("text"), str)
        ):
            raise ValueError("У каждой заметки должны быть целочисленный id > 0 и строковый text.")

    return notes


def save_notes(file_path: Path, notes: list[dict]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(notes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def search_notes(notes: list[dict], query: str) -> list[dict]:
    # Учебный баг: поиск должен игнорировать регистр, но здесь учитывает его.
    return [note for note in notes if query in note["text"]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Локальный блокнот с заметками в JSON.")
    parser.add_argument(
        "--file",
        type=Path,
        default=Path("notes.json"),
        help="Путь к хранилищу (по умолчанию: notes.json). Указывается перед командой.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", help="Добавить заметку.")
    add_parser.add_argument("text", help="Текст заметки в кавычках.")
    commands.add_parser("list", help="Показать все заметки.")
    search_parser = commands.add_parser("search", help="Найти заметки по подстроке.")
    search_parser.add_argument("query", help="Строка для поиска.")

    args = parser.parse_args()
    if args.command == "add" and not args.text.strip():
        parser.error("Текст заметки не может быть пустым.")
    if args.command == "search" and not args.query.strip():
        parser.error("Строка поиска не может быть пустой.")

    try:
        notes = load_notes(args.file)

        if args.command == "add":
            note_id = max((note["id"] for note in notes), default=0) + 1
            notes.append({"id": note_id, "text": args.text.strip()})
            save_notes(args.file, notes)
            print(f"Добавлена заметка #{note_id}.")
            return

        if args.command == "search":
            notes = search_notes(notes, args.query)

        if not notes:
            print("Совпадений нет." if args.command == "search" else "Заметок нет.")
            return

        for note in notes:
            print(f"#{note['id']}: {note['text']}")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Ошибка: {error}\n")


if __name__ == "__main__":
    main()
