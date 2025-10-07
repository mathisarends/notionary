def process_markdown_whitespace(markdown_text: str) -> str:
    """
    Normalize whitespace in markdown while preserving code block formatting.

    Regular text: Leading whitespace is removed
    Code blocks: Original indentation is preserved with common indent removed
    """
    if not markdown_text:
        return ""

    lines = markdown_text.split("\n")
    processed_lines = []
    code_block_lines = []
    in_code_block = False

    for line in lines:
        if _is_code_fence(line):
            if in_code_block:
                processed_lines.extend(_format_code_block(code_block_lines))
                processed_lines.append("```")
                code_block_lines = []
                in_code_block = False
            else:
                language = _extract_language(line)
                processed_lines.append(f"```{language}")
                in_code_block = True
        elif in_code_block:
            code_block_lines.append(line)
        else:
            processed_lines.append(line.lstrip())

    return "\n".join(processed_lines)


def _is_code_fence(line: str) -> bool:
    return line.lstrip().startswith("```")


def _extract_language(fence_line: str) -> str:
    return fence_line.lstrip().removeprefix("```").strip()


def _format_code_block(lines: list[str]) -> list[str]:
    """
    Format code block by removing common leading whitespace.

    Preserves relative indentation between lines.
    Empty lines are preserved as-is.
    """
    if not lines:
        return []

    non_empty_lines = [line for line in lines if line.strip()]
    if not non_empty_lines:
        return ["" for _ in lines]

    min_indent = min(_count_leading_spaces(line) for line in non_empty_lines)

    if min_indent == 0:
        return lines

    return [_remove_indent(line, min_indent) for line in lines]


def _count_leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip())


def _remove_indent(line: str, indent_size: int) -> str:
    if not line.strip():
        return ""
    return line[indent_size:]
