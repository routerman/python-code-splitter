from dataclasses import dataclass
from pathlib import Path

from src.entities.block import Block
from src.services.generate_import_statement_service import (
    GenerateImportStatementService,
)
from src.utils import git


@dataclass(frozen=True)
class GenerateInitFileService:
    moved_blocks: list[Block]
    init_file_path: Path
    git_commit: bool

    def execute(self) -> Path:
        new_dir_path = self.init_file_path.parent
        # Generate import statements for the moved Blocks
        import_statement = GenerateImportStatementService(
            new_dir_path=new_dir_path, moved_blocks=self.moved_blocks
        ).execute()
        # Add import statements to the existing __init__.py file
        with self.init_file_path.open(mode="r") as file:
            current_lines = file.readlines()
        # Generate a new __init__.py file
        with self.init_file_path.open(mode="w") as file:
            file.writelines(import_statement)
            file.writelines(current_lines)
            file.write('\n__all__ = [\n    "' + '",\n    "'.join([block.name for block in self.moved_blocks]) + '"\n]')
        if self.git_commit:
            git(f"add {new_dir_path}")
            git(f'commit -m "[Auto] Attached import statements to the splitted files in {new_dir_path}."')
        return self.init_file_path
