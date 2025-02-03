import re

from src.entities.block_pattern import BlockPattern
from src.enums.block_type import BlockType

BLOCK_START_PATTERN = re.compile(r"^[a-zA-Z_@#\(\)\"\'][a-zA-Z0-9_]*")

IMPORT_PATTERN = BlockPattern(name=BlockType.IMPORT, pattern=re.compile(r"^(import|from)\s+"))
FUNCTION_PATTERN = BlockPattern(name=BlockType.FUNCTION, pattern=re.compile(r"^(async\s+def|def)\s+([a-zA-Z0-9_]*)"))
CLASS_PATTERN = BlockPattern(name=BlockType.CLASS, pattern=re.compile(r"^class\s+([a-zA-Z0-9_]*)\s*[:\(]"))
VALUE_PATTERN = BlockPattern(name=BlockType.VALUE, pattern=re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*="))
COMMENT_PATTERN = BlockPattern(name=BlockType.COMMENT, pattern=re.compile(r"^\s*(#|\"\"\"|\'\'\')"))
