def indent_text(text: str, spaces: int = 4) -> str:
    if not text:
        return text

    indent = " " * spaces
    lines = text.split("\n")
    return "\n".join(f"{indent}{line}" if line.strip() else line for line in lines)
