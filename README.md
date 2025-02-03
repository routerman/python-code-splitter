# python-code-splitter

A script to split Python code by classes and functions.

## Process Flow

1. Extract class and function definitions from the target file into separate new files
  1. The file name will be {class name or function name converted to snake_case}.py
  2. Commit each move with git to make it easier to review
2. Move the remaining content of the target file to `__init__.py`
3. Add necessary import statements to the top of each file

## Features

- ⭕️ Moves decorators and comments as well
- ⭕️ Automatically creates a git branch based on the target file path
- ⭕️ Commits in review-friendly units

## Limitations

- ❌ No regression checks
- ❌ Does not group related classes nicely
- ❌ Does not remove unnecessary import statements
- ❌ Does not remove unnecessary variables and constants
- ❌ Does not resolve circular imports

## Notes

If there are comment lines mixed in the import statements, the splitting may not work correctly (remove them manually beforehand).
