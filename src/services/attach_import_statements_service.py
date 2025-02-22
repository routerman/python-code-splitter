from dataclasses import dataclass
from pathlib import Path

from src.entities.block import Block
from src.entities.file import File
from src.services.generate_import_statement_service import (
    GenerateImportStatementService,
)


@dataclass(frozen=True)
class AttachImportStatementsService:
    moved_files: list[File]
    non_moved_blocks: list[Block]
    new_dir_path: Path

    def execute(self):
        moved_files = sorted(self.moved_files, key=lambda file: (file.blocks[0].type, file.blocks[0].name))
        for moved_file in moved_files:
            import_statement = GenerateImportStatementService(
                new_dir_path=self.new_dir_path,
                moved_files=moved_files,
                non_moved_blocks=self.non_moved_blocks,
                exclude_file=moved_file,
            ).execute()
            text = moved_file.path.read_text()
            text = "".join(import_statement) + text
            moved_file.path.write_text(text)
