import re
from typing import Optional

UUID_PATTERN = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
UUID_RAW_PATTERN = r'([a-f0-9]{32})'


def extract_uuid(source: str) -> Optional[str]:
    match = re.search(UUID_RAW_PATTERN, source.lower())
    if not match:
        return None

    uuid_raw = match.group(1)
    return f"{uuid_raw[0:8]}-{uuid_raw[8:12]}-{uuid_raw[12:16]}-{uuid_raw[16:20]}-{uuid_raw[20:32]}"


def is_valid_uuid(uuid: str) -> bool:
    return bool(re.match(UUID_PATTERN, uuid.lower()))


def format_uuid(value: str) -> Optional[str]:
    if is_valid_uuid(value):
        return value
    return extract_uuid(value)
