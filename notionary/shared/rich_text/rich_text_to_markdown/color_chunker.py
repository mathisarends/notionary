from dataclasses import dataclass

from notionary.blocks.enums import BlockColor
from notionary.rich_text.schemas import RichText


@dataclass
class ColorGroup:
    color: BlockColor
    objects: list[RichText]


def chunk_by_color(rich_texts: list[RichText]) -> list[ColorGroup]:
    if not rich_texts:
        return []

    groups: list[ColorGroup] = []
    current_color = _extract_color(rich_texts[0])
    current_group: list[RichText] = []

    for obj in rich_texts:
        obj_color = _extract_color(obj)

        if obj_color == current_color:
            current_group.append(obj)
        else:
            groups.append(ColorGroup(color=current_color, objects=current_group))
            current_color = obj_color
            current_group = [obj]

    groups.append(ColorGroup(color=current_color, objects=current_group))
    return groups


def _extract_color(obj: RichText) -> BlockColor:
    if obj.annotations and obj.annotations.color:
        return obj.annotations.color
    return BlockColor.DEFAULT
