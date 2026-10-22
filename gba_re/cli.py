from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyze import byte_statistics, gba_rom_pointers, printable_strings, region_entropy
from .header import parse_header
from .rom import Rom


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gba-re",
        description="GBA ROM inspection and reverse-engineering workspace generator.",
    )
    parser.add_argument("rom", help="Path to the .gba ROM")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("--strings-min", type=int, default=4, help="Minimum ASCII string length (default: 4)")
    parser.add_argument("--no-rom-copy", action="store_true", help="Do not copy the original ROM into the workspace")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    rom = Rom.load(args.rom)
    header = parse_header(rom)

    name = header.game_code.strip() or rom.path.stem
    output = Path(args.output).expanduser().resolve() if args.output else Path("analysis") / name
    output.mkdir(parents=True, exist_ok=True)
    for directory in ("code", "data", "graphics", "audio", "strings", "pointers", "regions"):
        (output / directory).mkdir(exist_ok=True)

    if not args.no_rom_copy:
        (output / "rom.bin").write_bytes(rom.data)

    (output / "header.json").write_text(json.dumps(header.to_dict(), indent=2) + "\n")
    (output / "hashes.json").write_text(json.dumps(rom.hashes(), indent=2) + "\n")
    (output / "statistics.json").write_text(json.dumps(byte_statistics(rom.data), indent=2) + "\n")
    (output / "pointers" / "rom_pointers.json").write_text(json.dumps(gba_rom_pointers(rom.data), indent=2) + "\n")
    (output / "strings" / "ascii.json").write_text(json.dumps(printable_strings(rom.data, args.strings_min), indent=2) + "\n")
    (output / "regions" / "entropy_4k.json").write_text(json.dumps(region_entropy(rom.data), indent=2) + "\n")

    print(f"ROM:       {rom.path}")
    print(f"Title:     {header.title or '(unknown)'}")
    print(f"Game code: {header.game_code or '(unknown)'}")
    print(f"Size:      {rom.size:,} bytes")
    print(f"Output:    {output}")
    print("Analysis complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
