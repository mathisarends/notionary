import re


def validate_columns_syntax(markdown_text: str) -> None:
    if not re.search(r"::: columns", markdown_text):
        return

    columns_blocks = _extract_columns_blocks(markdown_text)

    for content in columns_blocks:
        column_matches = list(re.finditer(r"::: column(?:\s+([\d.]+))?(?:\s|$)", content))

        column_count = len(column_matches)

        if column_count < 2:
            raise ValueError(
                f"columns Container muss mindestens 2 column Blöcke enthalten, aber nur {column_count} gefunden"
            )

        ratios = extract_ratios(column_matches)
        validate_ratios(ratios, column_count)


def _extract_columns_blocks(markdown_text: str) -> list[str]:
    columns_blocks = []
    lines = markdown_text.split("\n")
    i = 0

    while i < len(lines):
        if lines[i].strip() == "::: columns":
            # Finde den passenden closing :::
            depth = 1
            start = i + 1
            i += 1

            while i < len(lines) and depth > 0:
                line = lines[i].strip()
                if line.startswith("::: "):
                    # Öffnet einen neuen Block
                    depth += 1
                elif line == ":::":
                    # Schließt einen Block
                    depth -= 1
                i += 1

            if depth == 0:
                # Wir haben den passenden closing ::: gefunden
                content = "\n".join(lines[start : i - 1])
                columns_blocks.append(content)
        else:
            i += 1

    return columns_blocks


def extract_ratios(column_matches) -> list[float]:
    ratios = []
    for match in column_matches:
        ratio_str = match.group(1)
        if ratio_str and ratio_str != "1":
            ratios.append(float(ratio_str))
    return ratios


def validate_ratios(ratios, column_count) -> None:
    if ratios and len(ratios) == column_count:
        total = sum(ratios)
        if abs(total - 1.0) > 0.0001:
            raise ValueError(f"width_ratios müssen sich zu 1.0 addieren, aber Summe ist {total}")
