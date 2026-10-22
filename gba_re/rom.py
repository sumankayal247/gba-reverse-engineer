from __future__ import annotations

from dataclasses import dataclass
from hashlib import md5, sha1, sha256
from pathlib import Path

GBA_HEADER_SIZE = 0xC0
ROM_BASE = 0x08000000


@dataclass(frozen=True)
class Rom:
    path: Path
    data: bytes

    @classmethod
    def load(cls, path: str | Path) -> "Rom":
        p = Path(path).expanduser().resolve()
        if not p.is_file():
            raise FileNotFoundError(f"ROM not found: {p}")
        if p.suffix.lower() != ".gba":
            raise ValueError("Input file must have a .gba extension")
        data = p.read_bytes()
        if len(data) < GBA_HEADER_SIZE:
            raise ValueError("File is too small to contain a GBA header")
        return cls(p, data)

    @property
    def size(self) -> int:
        return len(self.data)

    def hashes(self) -> dict[str, str]:
        return {
            "md5": md5(self.data).hexdigest(),
            "sha1": sha1(self.data).hexdigest(),
            "sha256": sha256(self.data).hexdigest(),
        }

    def slice(self, start: int, end: int) -> bytes:
        return self.data[start:end]
