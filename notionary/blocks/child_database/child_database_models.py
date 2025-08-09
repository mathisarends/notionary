from typing import Any
from pydantic import BaseModel, Field
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class CreateInlineDatabaseRequest(BaseModel):
    """
    Minimaler Create-Payload für eine inline Database.
    Parent wird von der Page-Schicht gesetzt: {"type": "page_id", "page_id": "..."}.
    """

    parent: dict[str, str]  # wird von außen injiziert
    title: list[
        RichTextObject
    ]  # z. B. [RichTextObject.from_plain_text("Monatsübersicht")]
    properties: dict[str, dict[str, Any]]  # mindestens eine Title-Property erforderlich
    is_inline: bool = True  # inline = erscheint als child_database-Block auf der Page
