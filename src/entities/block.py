from dataclasses import dataclass
from pathlib import Path

from src.enums.block_type import BlockType
from src.utils import to_snake_case


@dataclass()
class Block:
    type: BlockType
    name: str
    codes: list[str]

    def path(self, parent: Path) -> Path:
        return parent / self.file_name

    @property
    def file_name(self):
        if self.type == "class":
            return f"{to_snake_case(self.name)}.py"
        return f"{self.name}.py"
