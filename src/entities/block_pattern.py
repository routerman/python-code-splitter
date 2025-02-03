import re
from typing import NamedTuple

from src.enums.block_type import BlockType


class BlockPattern(NamedTuple):
    name: BlockType
    pattern: re.Pattern
