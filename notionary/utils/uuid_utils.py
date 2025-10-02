import re


def extract_uuid(source: str) -> str | None:
    UUID_RAW_PATTERN = r"([a-f0-9]{32})"

    if _is_valid_uuid(source):
        return source

    match = re.search(UUID_RAW_PATTERN, source.lower())
    if not match:
        return None

    uuid_raw = match.group(1)
    return f"{uuid_raw[0:8]}-{uuid_raw[8:12]}-{uuid_raw[12:16]}-{uuid_raw[16:20]}-{uuid_raw[20:32]}"


def _is_valid_uuid(uuid: str) -> bool:
    UUID_PATTERN = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    return bool(re.match(UUID_PATTERN, uuid.lower()))
