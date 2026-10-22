from __future__ import annotations

from collections import Counter
import math
import struct

from .rom import ROM_BASE, Rom


def printable_strings(data: bytes, minimum: int = 4) -> list[dict]:
    results = []
    start = None
    for i, byte in enumerate(data):
        printable = 32 <= byte <= 126
        if printable and start is None:
            start = i
        elif not printable and start is not None:
            if i - start >= minimum:
                results.append({"offset": start, "length": i - start, "text": data[start:i].decode("ascii")})
            start = None
    if start is not None and len(data) - start >= minimum:
        results.append({"offset": start, "length": len(data) - start, "text": data[start:].decode("ascii")})
    return results


def gba_rom_pointers(data: bytes) -> list[dict]:
    found = []
    for offset in range(0, len(data) - 3, 4):
        value = struct.unpack_from("<I", data, offset)[0]
        if ROM_BASE <= value < ROM_BASE + len(data):
            found.append({"file_offset": offset, "value": f"0x{value:08X}", "target_offset": value - ROM_BASE})
    return found


def byte_statistics(data: bytes) -> dict:
    counts = Counter(data)
    total = len(data)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return {
        "entropy_bits_per_byte": round(entropy, 6),
        "unique_bytes": len(counts),
        "zero_ratio": round(counts[0] / total, 6),
    }


def region_entropy(data: bytes, chunk_size: int = 0x1000) -> list[dict]:
    regions = []
    for start in range(0, len(data), chunk_size):
        chunk = data[start:start + chunk_size]
        regions.append({
            "offset": start,
            "size": len(chunk),
            "entropy": byte_statistics(chunk)["entropy_bits_per_byte"],
        })
    return regions
