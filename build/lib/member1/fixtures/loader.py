import json
from pathlib import Path

def load_fixture(name: str) -> list[dict]:
    """
    Loads a JSON fixture by name from member1/fixtures/data/{name}.json.

    Args:
        name: Name of the fixture (without .json extension).

    Returns:
        list[dict]: Parsed fixture content.

    Raises:
        FileNotFoundError: If the specified fixture does not exist.
        ValueError: If fixture name contains invalid path traversal characters.
    """
    if "/" in name or "\\" in name or ".." in name:
        raise ValueError(f"Invalid fixture name: '{name}'. Path traversal characters are forbidden.")

    base_dir = Path(__file__).parent / "data"
    file_path = base_dir / f"{name}.json"

    if not file_path.is_file():
        raise FileNotFoundError(f"Fixture '{name}' not found at path: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Fixture '{name}' must contain a JSON list at root.")

    return data
