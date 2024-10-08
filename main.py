import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class Block:
    codes: list[str]
    name: str
    type: Literal["other", "class", "function"]

    @property
    def file_name(self):
        if self.type == "class":
            return f"{to_snake_case(self.name)}.py"
        return f"{self.name}.py"
    
    def import_path(self, new_dir_path: Path):
        new_dir_path = str(new_dir_path).replace("/", ".")
        return f"from {new_dir_path}.{to_snake_case(self.name)} import {self.name}"


def shell_command(command: str):
    print(command)
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception(f"Failed to execute the command: {command}. {result.stderr=}")
    return result.stdout.decode("utf-8")


# クラス名をスネークケースに変換する関数
def to_snake_case(class_name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

# Blockインスタンスを生成する関数
def generate_block(codes: list[str]) -> Block:
    for code in codes:
        if code.startswith("class "):
            class_pattern = re.compile(r"^class\s+([A-Z][a-zA-Z0-9]*)\s*[:\(]")
            match = class_pattern.match(code)
            class_name = match and match.group(1)
            return Block(codes=codes, name=class_name, type="class")
        elif code.startswith("def "):
            def_pattern = re.compile(r"^def\s+([a-z][a-zA-Z0-9_]*)")  # \s*[:\(]')
            match = def_pattern.match(code)
            def_name = match and match.group(1)
            return Block(codes=codes, name=def_name, type="function")
    return Block(codes=codes, name="other", type="other")

def split_source_code(file_path: Path) -> list[Block]:
    """ファイルを読み込んでクラス・関数・それ以外に分割する"""
    with file_path.open() as file:
        lines = file.readlines()
    blocks: list[Block] = []
    codes = []
    in_decorator = False
    for line in lines:
        if line.startswith("class ") or line.startswith("def ") or line.startswith("@") or line.startswith("#"):
            # 冒頭のimport文群を取得
            if not blocks:
                if line.startswith("@") or line.startswith("#"):
                    in_decorator = True
                blocks.append(generate_block(codes))
                codes = [line]
                continue
            # デコレーターかコメントの中でなければ即分割
            if not in_decorator:
                if line.startswith("@") or line.startswith("#"):
                    in_decorator = True
                blocks.append(generate_block(codes))
                codes = [line]
                continue
            # デコレーターが終わったらフラグを下げる
            if in_decorator and (line.startswith("class ") or line.startswith("def ")):
                in_decorator = False
        codes.append(line)
    else:
        # 最後のブロックを追加
        blocks.append(generate_block(codes))
    # 分割後のブロック行数の合計が元の行数と一致するかチェック
    assert len(lines) == sum([len(block.codes) for block in blocks])
    return blocks


def generate_init_file(init_file_path: Path, blocks: list[Block]) -> Path:
    # 新しい__init__.pyファイルを生成する
    with init_file_path.open(mode="w") as init_file:
        for block in blocks:
            init_file.writelines(block.codes)
        init_file.write(f'\n__all__ = [\n    "' + '",\n    "'.join(sorted([block.name for block in blocks if block.type in ['class', 'function']])) + '"\n]')
    return init_file_path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python classi.py <path_to_python_file>")
        sys.exit(1)

    original_file_path = Path(sys.argv[1])
    if not original_file_path.exists() and not original_file_path.is_file():
        print(f"Error: File '{original_file_path}' does not exist.")
        sys.exit(1)

    # ファイルの移動先ディレクトリを作成
    new_dir_path = original_file_path.parent / original_file_path.stem
    new_dir_path.mkdir(parents=True, exist_ok=True)
    # ファイルをパースしてブロックに分割
    blocks = split_source_code(file_path=original_file_path)
    # ブロックのインポート文を生成し、追加
    imports_block = generate_block(
        codes=[block.import_path(new_dir_path) + '\n' for block in blocks if block.type in ["class"]]
    )
    # 特定タイプのブロックのみを別ファイルに移動
    class_blocks = list(filter(lambda block: block.type in ["class"], blocks))
    new_file_paths = []
    while class_blocks:
        block = class_blocks.pop()
        # 移動先ファイルを作成
        new_file_path = new_dir_path / block.file_name
        new_file_paths.append(new_file_path)
        with new_file_path.open(mode="w") as f:
            f.writelines(block.codes)
        # 残ブロックを元ファイルに書き戻す
        with original_file_path.open(mode="w") as f:
            for block in class_blocks:
                f.writelines(block.codes)
        # commit
        shell_command(f"git add {new_dir_path.parent}")
        shell_command(f'git commit -m "Move {block.type} {block.name} to {new_dir_path / block.file_name}."')

    init_file_path = new_dir_path / "__init__.py"
    # 各新規ファイルの先頭にother_blocksを追記
    for new_file_path in new_file_paths:
        with new_file_path.open(mode="r") as f:
            lines = f.readlines()
        with new_file_path.open(mode="w") as f:
            for block in [imports_block] + [block for block in blocks if block.type == "other"]:
                f.writelines(block.codes)
            f.writelines(lines)
    # __init__.pyファイルを生成
    shell_command(f"git mv {original_file_path} {init_file_path}")
    generate_init_file(
        init_file_path=init_file_path, blocks=blocks, 
    )
    shell_command(f"git add {init_file_path}")
    shell_command(f'git commit -m "generate {init_file_path}"')
