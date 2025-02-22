from dataclasses import dataclass

from src.enums.block_type import BlockType
from src.utils import to_snake_case


@dataclass(frozen=True)
class Block:
    type: BlockType
    name: str
    codes: list[str]

    @property
    def file_name(self):
        if self.type == "class":
            return f"{to_snake_case(self.name)}.py"
        return f"{self.name}.py"
