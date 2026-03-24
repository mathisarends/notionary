from dataclasses import dataclass


@dataclass(frozen=True)
class SyntaxPromptData:
    element: str
    description: str
    is_multi_line: bool
    few_shot_examples: list[str]
    usage_notes: str
    supports_inline_rich_text: bool
