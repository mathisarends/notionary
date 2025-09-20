import random
from typing import Sequence

DEFAULT_NOTION_COVERS: Sequence[str] = [
    f"https://www.notion.so/images/page-cover/gradients_{i}.png"
    for i in range(1, 10)
]

def get_random_gradient_cover(
    covers: Sequence[str] = DEFAULT_NOTION_COVERS,
) -> str:
    return random.choice(covers)
