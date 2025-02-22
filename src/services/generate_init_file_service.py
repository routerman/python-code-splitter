from dataclasses import dataclass
from pathlib import Path

from src.entities.file import File
from src.services.generate_import_statement_service import (
    GenerateImportStatementService,
)


@dataclass(frozen=True)
class UpdateInitFileService:
    init_file_path: Path
    moved_files: list[File]

    def execute(self) -> str:
        # Generate import statements for the moved Blocks
        original_init_file_text = self.init_file_path.read_text()
        import_statement = GenerateImportStatementService(
            new_dir_path=self.init_file_path.parent, moved_files=self.moved_files
        ).execute()
        all_text = (
            '\n__all__ = [\n    "'
            + '",\n    "'.join([block.name for file in self.moved_files for block in file.blocks])
            + '"\n]'
        )
        # Update __init__.py file
        new_init_file_text = "".join(import_statement) + original_init_file_text + all_text
        self.init_file_path.write_text(new_init_file_text)
        return new_init_file_text
