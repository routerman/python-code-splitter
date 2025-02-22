from dataclasses import dataclass
from pathlib import Path

from src.entities.block import Block
from src.entities.file import File
from src.enums.block_type import BlockType
from src.services.attach_import_statements_service import AttachImportStatementsService
from src.services.generate_init_file_service import UpdateInitFileService
from src.services.generate_new_git_branch_name_service import (
    GenerateNewGitBranchNameService,
)
from src.services.load_file_service import LoadFileService
from src.services.move_blocks_service import MoveBlocksToNewFilesService
from src.utils import git


@dataclass(frozen=True)
class CodeSplitter:
    original_file_path: Path
    git_commit: bool

    def execute(self):
        # 1. Load the target file
        original_file: File = LoadFileService(file_path=self.original_file_path).execute()

        # 2 Create new git branch
        if self.git_commit:
            branch_name = GenerateNewGitBranchNameService(original_file_path=original_file.path).execute()
            git(f"checkout -b {branch_name}")

        # 3. Move class and function definitions from the original file to new files one by one
        def git_commit_for_each_move(new_file: File, old_file: File, block: Block):
            if self.git_commit:
                # NOTE: Committed temporarily to avoid creating diffs for reviewers
                git(f"add {new_file.path} {old_file.path}")
                git(f'commit -m "[Auto] Move {block.type} {block.name} to {new_file.path}."')

        result = MoveBlocksToNewFilesService(
            original_file=original_file,
            target_block_types=[BlockType.CLASS, BlockType.FUNCTION],
            handler_for_each_move=git_commit_for_each_move,
        ).execute()

        # 4. Move the original file to __init__.py
        init_file_path = original_file.path.parent / original_file.path.stem / "__init__.py"
        git(f"mv {original_file.path} {init_file_path}")
        if self.git_commit:
            git(f"add {init_file_path}")
            git(f'commit -m "[Auto] git mv {original_file.path} {init_file_path}"')

        # 5. Add necessary import statements to the top of each file
        AttachImportStatementsService(
            moved_files=result.new_files,
            non_moved_blocks=result.old_file.blocks,
            new_dir_path=init_file_path.parent,
        ).execute()
        if self.git_commit:
            git(f"add {init_file_path.parent}")
            git(f'commit -m "[Auto] Attached import statements to the splitted files in {init_file_path.parent}."')

        # 6. Add import statements to the __init__.py file
        UpdateInitFileService(
            init_file_path=init_file_path,
            moved_files=result.new_files,
        ).execute()
        if self.git_commit:
            git(f"add {init_file_path}")
            git(f'commit -m "[Auto] Attached import statements to the splitted files in {init_file_path}."')
