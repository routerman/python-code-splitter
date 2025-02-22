from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GenerateNewGitBranchNameService:
    original_file_path: Path

    def execute(self) -> str:
        # Create the destination directory for the file
        path = self.original_file_path.parent / self.original_file_path.stem
        path_str = str(path).replace("/", "_").replace(".py", "")
        branch_name = "split/" + path_str
        return branch_name
