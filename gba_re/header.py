from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import struct

from .rom import Rom


@dataclass(frozen=True)
class GbaHeader:
    entry_point: str
    logo_valid: bool
    title: str
    game_code: str
    maker_code: str
    fixed_value: int
    main_unit_code: int
    device_type: int
    software_version: int
    complement_check: int
    header_checksum: int
    header_checksum_valid: bool

    def to_dict(self) -> dict:
        return asdict(self)


def parse_header(rom: Rom) -> GbaHeader:
    d = rom.data
    entry = d[0:4].hex()
    logo = d[4:0xA0]
    title = d[0xA0:0xAC].rstrip(b"\0").decode("ascii", "replace")
    game_code = d[0xAC:0xB0].decode("ascii", "replace")
    maker = d[0xB0:0xB2].decode("ascii", "replace")
    fixed = d[0xB2]
    main_unit = d[0xB3]
    device = d[0xB4]
    version = d[0xBC]
    complement = d[0xBD]
    checksum = d[0xBE]

    calc = 0
    for value in d[0xA0:0xBD]:
        calc = (calc - value) & 0xFF
    calc = (calc - 0x19) & 0xFF

    return GbaHeader(
        entry_point=entry,
        logo_valid=logo == bytes.fromhex(
            "24ffae51699aa2213d84820a84e409ad11248b98c0817f21a352be199e7db3c"
            "825a3d4f837c9e5f8f3f0a9e3f6f3c1c"
        )[:156],
        title=title,
        game_code=game_code,
        maker_code=maker,
        fixed_value=fixed,
        main_unit_code=main_unit,
        device_type=device,
        software_version=version,
        complement_check=complement,
        header_checksum=checksum,
        header_checksum_valid=calc == checksum,
    )


def dump_header(rom: Rom, path) -> None:
    path.write_text(json.dumps(parse_header(rom).to_dict(), indent=2) + "\n")
