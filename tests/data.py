from pathlib import Path


def resolve_path(filename: str) -> str:
    result = str(Path(__file__).parent / filename)
    return result
