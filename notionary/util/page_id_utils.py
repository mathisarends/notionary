import re
from typing import Optional

UUID_PATTERN = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
UUID_RAW_PATTERN = r"([a-f0-9]{32})"


def extract_uuid(source: str) -> Optional[str]:
    if is_valid_uuid(source):
        return source

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


def extract_and_validate_page_id(page_id: Optional[str], url: Optional[str]) -> str:
    if not page_id and not url:
        raise ValueError("Either page_id or url must be provided")

    candidate = page_id or url

    if is_valid_uuid(candidate):
        return candidate

    extracted_id = extract_uuid(candidate)
    if not extracted_id:
        raise ValueError(f"Could not extract a valid UUID from: {candidate}")

    formatted = format_uuid(extracted_id)
    if not formatted or not is_valid_uuid(formatted):
        raise ValueError(f"Invalid UUID format: {formatted}")
    return formatted
