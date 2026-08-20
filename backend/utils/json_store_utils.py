import json
from pathlib import Path
from collections.abc import Iterator, MutableMapping
from typing import Any


class JsonStore(MutableMapping[str, Any]):
    """JSONファイルを永続化先として使用する辞書型ストア"""

    def __init__(self, filepath: str | Path):
        self.path = Path(filepath)
        self._data: dict[str, Any] = {}

        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as f:
                self._data = json.load(f)

    def save(self) -> None:
        """現在の内容をJSONファイルへ保存する。"""
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    # ----- MutableMapping -----

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)
