import argparse
from pathlib import Path

from src.code_splitter import CodeSplitter


def main():
    parser = argparse.ArgumentParser(description="Python Code Splitter")
    parser.add_argument("file_path", type=str, help="Path to the Python file to split")
    parser.add_argument("--git", action="store_true", help="Enable git commit")
    args = parser.parse_args()

    CodeSplitter(original_file_path=Path(args.file_path), git_commit=args.git).execute()


if __name__ == "__main__":
    main()
