from pydantic import BaseModel

class ExternalFile(BaseModel):
    """Represents an external file, e.g., for cover images."""

    url: str