from dataclasses import dataclass
from pathlib import Path

from src.entities.block import Block
from src.entities.file import File
from src.enums.block_type import BlockType
from src.utils import git


def get_new_git_branch_name(path: Path) -> str:
    return f"split/{str(path).replace('/', '_').replace('.py', '')}"


@dataclass(frozen=True)
class MoveBlocksToNewFilesService:
    original_file: File
    target_block_types: list[BlockType]
    git_commit: bool

    def execute(self) -> tuple[list[Block], list[Block]]:
        # Create the destination directory for the file
        new_dir_path = self.original_file.path.parent / self.original_file.path.stem
        if self.git_commit:
            branch_name = get_new_git_branch_name(path=new_dir_path)
            git(f"checkout -b {branch_name}")
        new_dir_path.mkdir(parents=True, exist_ok=True)

        # Move each class (function) from the input file to individual new files
        moved_blocks, non_moved_blocks = [], []
        blocks = self.original_file.blocks
        while blocks:
            block = blocks.pop()
            if block.type not in self.target_block_types:
                # Leave other blocks as they are
                non_moved_blocks.append(block)
                continue
            # Create the destination file
            with block.path(parent=new_dir_path).open(mode="w") as f:
                f.writelines(block.codes)
            # Write remaining blocks back to the original file
            with self.original_file.path.open(mode="w") as f:
                for rest_block in blocks + list(reversed(non_moved_blocks)):
                    f.writelines(rest_block.codes)
            if self.git_commit:
                # NOTE: Committed temporarily to avoid creating diffs for reviewers
                git(f"add {block.path(parent=new_dir_path)}")
                git(f"add {self.original_file.path}")
                git(f'commit -m "[Auto] Move {block.type} {block.name} to {block.path(parent=new_dir_path)}."')
            moved_blocks.append(block)
        return moved_blocks, non_moved_blocks
