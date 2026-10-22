# GBA Reverse Engineer

A Linux-first Python toolkit for inspecting and progressively reverse-engineering Game Boy Advance (`.gba`) ROMs.

> **Status:** early development (`v0.1.0`). This is an analysis toolkit, not a magic one-click decompiler. It builds a reproducible workspace containing ROM metadata, hashes, candidate pointers, ASCII strings, and entropy regions. More GBA-specific analyzers will be added incrementally.

## What it does now

Given a `.gba` file, the CLI:

- validates and loads the ROM
- reads the standard GBA header
- reports title, game code, maker code, version, and header checksum
- calculates MD5, SHA-1, and SHA-256 hashes
- copies the ROM into an isolated analysis workspace by default
- scans for 32-bit little-endian pointers into the GBA ROM address space
- extracts printable ASCII strings
- calculates whole-ROM byte statistics and entropy
- calculates entropy for 4 KiB regions
- creates directories for future code/data/graphics/audio analysis
- writes machine-readable JSON so later tools can consume the results

## Linux installation — step by step

### 1. Install Git and Python

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
```

Check the versions:

```bash
python3 --version
git --version
```

Python 3.10 or newer is required.

### 2. Clone the repository

```bash
git clone https://github.com/sumankayal247/gba-reverse-engineer.git
cd gba-reverse-engineer
```

### 3. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

After activation your shell should show something similar to:

```text
(.venv) user@computer:~/gba-reverse-engineer$
```

### 4. Install the project

This project currently has no third-party runtime dependencies.

Install it in editable mode:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

You can now use the `gba-re` command.

### 5. Verify the CLI

```bash
gba-re --help
```

You should see the available options and the ROM positional argument.

## Running the analyzer

Give the CLI the path to a GBA ROM:

```bash
gba-re /path/to/game.gba
```

Example:

```bash
gba-re ~/ROMs/my-game.gba
```

By default the analysis is written to:

```text
analysis/<GAME_CODE>/
```

For example:

```text
analysis/XXXX/
├── audio/
├── code/
├── data/
├── graphics/
├── pointers/
│   └── rom_pointers.json
├── regions/
│   └── entropy_4k.json
├── strings/
│   └── ascii.json
├── hashes.json
├── header.json
├── rom.bin
└── statistics.json
```

### Choose an output directory

```bash
gba-re ~/ROMs/my-game.gba --output ./work/my-game
```

### Do not duplicate the ROM

The default behavior copies the input ROM into `rom.bin` so the analysis directory is self-contained. If you do not want that copy:

```bash
gba-re ~/ROMs/my-game.gba --no-rom-copy
```

### Change the minimum ASCII string length

Default is 4 characters:

```bash
gba-re ~/ROMs/my-game.gba --strings-min 6
```

## Running without installing the command

You can also run it directly from the repository:

```bash
python3 -m gba_re.cli ~/ROMs/my-game.gba
```

## Understanding the output

### `header.json`

Contains information from the GBA cartridge header, including:

- entry point bytes
- game title
- game code
- maker code
- software version
- header checksum

### `hashes.json`

Cryptographic fingerprints of the complete input ROM:

- MD5
- SHA-1
- SHA-256

These are useful for identifying exactly which ROM revision was analyzed.

### `pointers/rom_pointers.json`

The first pointer pass treats values in the form `0x08000000 + offset` as possible ROM pointers. Every result contains the source file offset and calculated target offset.

These are **candidates**, not guaranteed pointers. Later analysis will distinguish actual pointers from coincidental byte patterns.

### `strings/ascii.json`

Contains runs of printable ASCII characters together with their ROM offsets. Pokémon and other GBA games can use custom text encodings, so this is deliberately only the first string pass.

### `regions/entropy_4k.json`

The ROM is divided into 4 KiB regions and an entropy value is calculated for each region. Entropy is useful as a heuristic when looking for compressed or highly structured data, but it does not by itself identify a region's type.

## Development roadmap

The project will progressively move from generic binary inspection toward GBA-aware reverse engineering:

1. GBA header and ROM mapping
2. ARM/Thumb code discovery
3. function boundary and branch analysis
4. literal-pool detection
5. pointer/reference graphs
6. common GBA compression detection and decompression
7. graphics/tile/palette detection
8. map and tilemap analysis
9. text-encoding detection
10. script/event analysis
11. data-table discovery
12. audio structure analysis
13. cross-reference database
14. interactive HTML/JSON reports
15. emulator-assisted validation
16. game-specific structures and labels

The long-term goal is a **reproducible reverse-engineering workspace**, not merely a ROM extractor.

## Safety and legal note

Only analyze ROMs you are legally permitted to possess and analyze. Do not commit copyrighted ROM files or extracted proprietary assets to this repository. The tool itself is intended to be open-source; ROMs and generated proprietary assets should remain outside version control unless you have the necessary rights.
