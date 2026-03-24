from dataclasses import dataclass


@dataclass
class PersonUser:
    id: str
    name: str
    email: str
    avatar_url: str | None = None


@dataclass
class BotUser:
    id: str
    name: str | None
    workspace_name: str | None
    workspace_file_upload_limit_in_bytes: int
    avatar_url: str | None = None
