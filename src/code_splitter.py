from dataclasses import dataclass
from pathlib import Path

from src.entities.file import File
from src.enums.block_type import BlockType
from src.services.attach_import_statements_service import AttachImportStatements
from src.services.generate_init_file_service import GenerateInitFileService
from src.services.load_file_service import LoadFileService
from src.services.move_blocks_service import MoveBlocksToNewFilesService


@dataclass(frozen=True)
class CodeSplitter:
    original_file_path: Path
    git_commit: bool

    def execute(self):
        # 1. Load the target file
        original_file: File = LoadFileService(file_path=self.original_file_path).execute()
        # 2. Extract class and function definitions from the target file into new files one by one
        moved_blocks, non_moved_blocks = MoveBlocksToNewFilesService(
            original_file=original_file,
            target_block_types=[BlockType.CLASS, BlockType.FUNCTION],
            git_commit=self.git_commit,
        ).execute()
        # 3. Move the remaining target file to {stem}/__init__.py
        init_file_path: Path = original_file.move_to_init(git_commit=self.git_commit)
        # 4. Add necessary import statements to the top of each file
        AttachImportStatements(
            moved_blocks=moved_blocks,
            non_moved_blocks=non_moved_blocks,
            new_dir_path=init_file_path.parent,
        ).execute()
        # 5. Add import statements to the __init__.py file
        GenerateInitFileService(
            moved_blocks=moved_blocks,
            init_file_path=init_file_path,
            git_commit=self.git_commit,
        ).execute()
