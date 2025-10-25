from dataclasses import dataclass


@dataclass(frozen=True)
class SyntaxPromptData:
    description: str
    is_multi_line: bool
    few_shot_examples: list[str]
