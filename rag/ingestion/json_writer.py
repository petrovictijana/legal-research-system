
import json
import os


def save_json(data: dict, output_path: str) -> None:
    """
    Saves a Python dictionary as a UTF-8 JSON file.
    """

    directory = os.path.dirname(output_path)

    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )
