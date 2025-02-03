from dataclasses import dataclass
from pathlib import Path

from src.entities.block import Block
from src.utils import git


@dataclass(frozen=True)
class File:
    path: Path
    blocks: list[Block]

    def move(self, to: Path, git_commit: bool) -> Path:
        if to.exists():
            raise FileExistsError(f"Error: File '{to}' already exists.")
        if git_commit:
            git(f"mv {self.path} {to}")
            git(f"add {to}")
            git(f'commit -m "[Auto] git mv {self.path} {to}"')
        else:
            self.path.rename(to)
        return to

    def move_to_init(self, git_commit: bool) -> Path:
        init_file_path = self.path.parent / self.path.stem / "__init__.py"
        return self.move(to=init_file_path, git_commit=git_commit)
