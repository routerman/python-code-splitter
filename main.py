"""
djangoプロジェクトのpythonコードをクラス・関数ごとに切り分けるスクリプトです。

## 使い方

python django_code_splitter.py path/to/models.py

## 処理の流れ

1. 対象のファイルから、クラス定義・関数定義を1つずつ新規ファイルに切り出す
  - ファイル名は {クラス名・関数名をスネークケースに変換したもの}.py
  - レビューしやすいように1移動ごとにgit commit
3. 残った対象のファイルを__init__.pyに移動
4. 必要そうなインポート文を各ファイルの先頭に付加

## やってくれること

⭕️ デコレータやコメントも移動する
⭕️ 対象のファイルパスを元にgit branchを自動で作成
⭕️ レビューしやすい単位でgit commit
⭕️ 間接importの解消（"やってくれる"というか、エラーが起きます）

## やらないこと

❌ デグレチェック
❌ QuerySetクラスやChoicesクラスを、関連するモデルクラスとイイ感じにまとめる
❌ 不要なimport文の削除
❌ 不要な変数・定数の削除
❌ 循環importの解消

## 注意点

import文の中にコメント行が混ざってると上手く分割できません(予め手動で消しとけばOK)
"""

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

GIT_COMMIT = True
ROOT_PATH = "."


def shell_command(command: str):
    print(command)
    if not GIT_COMMIT and command.startswith("git"):
        return
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception(f"Failed to execute the command: {command}. {result.stderr=}")
    return result.stdout.decode("utf-8")


# クラス名をスネークケースに変換する関数
def to_snake_case(class_name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


@dataclass
class Block:
    codes: list[str]
    name: str
    type: Literal["other", "class", "function"]

    def __init__(self, codes: list[str]):
        self.codes = codes
        for code in codes:
            if code.startswith("class "):
                class_pattern = re.compile(r"^class\s+([A-Z][a-zA-Z0-9]*)\s*[:\(]")
                match = class_pattern.match(code)
                class_name = match and match.group(1)
                self.name = class_name
                self.type = "class"
                break
            elif code.startswith("def "):
                def_pattern = re.compile(r"^def\s+([a-z][a-zA-Z0-9_]*)")  # \s*[:\(]')
                match = def_pattern.match(code)
                def_name = match and match.group(1)
                self.name = def_name
                self.type = "function"
                break
        else:
            self.name = "other"
            self.type = "other"

    def path(self, parent: Path) -> Path:
        return parent / self.file_name

    @property
    def file_name(self):
        if self.type == "class":
            return f"{to_snake_case(self.name)}.py"
        return f"{self.name}.py"

    def import_path(self, new_dir_path: Path):
        new_dir_path = str(new_dir_path).replace(ROOT_PATH, "").replace("/", ".")
        return f"from {new_dir_path}.{to_snake_case(self.name)} import {self.name}"


class DjangoCodeSplitter:

    @classmethod
    def execute(cls, original_file_path: Path):
        blocks = DjangoCodeSplitter.load(file_path=original_file_path)
        # 1. 対象のファイルから、クラス定義・関数定義を1つずつ新規ファイルに切り出す
        moved_blocks = DjangoCodeSplitter.move_blocks_to_new_files(blocks=blocks, original_file_path=original_file_path)
        # 2. 残った対象のファイルを__init__.pyに移動
        init_file_path = DjangoCodeSplitter.move_original_file_to_init_file(original_file_path=original_file_path)
        # 3. 必要そうなインポート文を各ファイルの先頭に付加
        DjangoCodeSplitter.attach_import_statements(moved_blocks=moved_blocks, init_file_path=init_file_path)

    @classmethod
    def load(cls, file_path: Path) -> list[Block]:
        """ファイルを読み込んでクラス・関数・それ以外に分割する"""
        assert file_path.is_file(), f"Error: File '{file_path}' does not exist."
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
                    blocks.append(Block(codes=codes))
                    codes = [line]
                    continue
                # デコレーターかコメントの中でなければ即分割
                if not in_decorator:
                    if line.startswith("@") or line.startswith("#"):
                        in_decorator = True
                    blocks.append(Block(codes=codes))
                    codes = [line]
                    continue
                # デコレーターが終わったらフラグを下げる
                if in_decorator and (line.startswith("class ") or line.startswith("def ")):
                    in_decorator = False
            codes.append(line)
        else:
            # 最後のブロックを追加
            blocks.append(Block(codes=codes))
        # 分割後のブロック行数の合計が元の行数と一致するかチェック
        assert len(lines) == sum([len(block.codes) for block in blocks])
        return blocks

    @classmethod
    def move_blocks_to_new_files(cls, blocks: list[Block], original_file_path: Path) -> list[Block]:
        # ファイルの移動先ディレクトリを作成
        new_dir_path = original_file_path.parent / original_file_path.stem
        assert not new_dir_path.is_dir(), f"Error: Directory '{new_dir_path}' already exists."
        if GIT_COMMIT:
            branch_name = f"refactor/dcs_{str(original_file_path).replace('/', '_').replace('.py', '')}"
            shell_command(f"git checkout -b {branch_name}")
        new_dir_path.mkdir(parents=True, exist_ok=True)

        # 入力ファイルから1クラス(関数)ずつ個別の新規ファイルに移動
        moved_blocks, other_blocks = [], []
        while blocks:
            block = blocks.pop()
            if block.type == "other":
                # その他のブロックはそのまま残す
                other_blocks.append(block)
                continue
            # 移動先ファイルを作成
            with block.path(parent=new_dir_path).open(mode="w") as f:
                f.writelines(block.codes)
            # 残ブロックを元ファイルに書き戻す
            with original_file_path.open(mode="w") as f:
                for rest_block in blocks:
                    f.writelines(rest_block.codes)
            if GIT_COMMIT:
                # NOTE: レビュワーのため、差分を作らないようにコピーしただけで一旦コミット
                shell_command(f"git add {block.path(parent=new_dir_path)}")
                shell_command(f"git add {original_file_path}")
                shell_command(
                    f'git commit -m "[dcs] Move {block.type} {block.name} to {block.path(parent=new_dir_path)}."'
                )
            moved_blocks.append(block)
        return moved_blocks

    @classmethod
    def move_original_file_to_init_file(cls, original_file_path: Path) -> Path:
        # 残った入力ファイルを__init__.pyファイルに移動
        init_file_path = original_file_path.parent / original_file_path.stem / "__init__.py"
        if GIT_COMMIT:
            shell_command(f"git mv {original_file_path} {init_file_path}")
            shell_command(f"git add {init_file_path}")
            shell_command(f'git commit -m "[dcs] git mv {original_file_path} {init_file_path}"')
        else:
            original_file_path.rename(init_file_path)
        return init_file_path

    @classmethod
    def attach_import_statements(cls, moved_blocks: list[Block], init_file_path: Path):
        # 各新規ファイルの先頭に追記する(不要なものはlinterで削除される想定)
        with init_file_path.open(mode="r") as f:
            init_file_codes = f.readlines()
        new_dir_path = init_file_path.parent
        moved_blocks = sorted(moved_blocks, key=lambda block: block.name)
        for moved_block in moved_blocks:
            with moved_block.path(parent=new_dir_path).open(mode="w") as f:
                import_statement = cls.generate_import_statement_of_moved_blocks(
                    new_dir_path=new_dir_path,
                    moved_blocks=moved_blocks,
                    exclude_block=moved_block,
                )
                f.writelines(import_statement)
                f.writelines(init_file_codes)
                f.writelines(moved_block.codes)

        # __init__.pyファイルにもインポート文を追加する
        cls.generate_init_file(
            init_file_path=init_file_path,
            moved_blocks=moved_blocks,
        )
        shell_command(f"git add {init_file_path.parent}")
        shell_command(f'git commit -m "[dcs] Attached import statements to the splitted files in {new_dir_path}."')

    @classmethod
    def generate_init_file(cls, init_file_path: Path, moved_blocks: list[Block]) -> Path:
        # 新しい__init__.pyファイルを生成する
        with init_file_path.open(mode="r") as file:
            current_lines = file.readlines()
        import_statement = cls.generate_import_statement_of_moved_blocks(
            new_dir_path=init_file_path.parent, moved_blocks=moved_blocks
        )
        with init_file_path.open(mode="w") as file:
            file.writelines(import_statement)
            file.writelines(current_lines)
            file.write(f'\n__all__ = [\n    "' + '",\n    "'.join([block.name for block in moved_blocks]) + '"\n]')
        return init_file_path

    @classmethod
    def generate_import_statement_of_moved_blocks(
        cls, new_dir_path: Path, moved_blocks: list[Block], exclude_block: Block = None
    ) -> list[str]:
        # 移動したブロックへのインポート文を生成
        import_statement = []
        for block in moved_blocks:
            if exclude_block and block.name == exclude_block.name:
                continue
            import_statement.append(block.import_path(new_dir_path=new_dir_path) + "\n")
        return import_statement


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python django_code_splitter.py path/to/models.py")
        sys.exit(1)
    original_file_path = Path(sys.argv[1])
    DjangoCodeSplitter.execute(original_file_path=original_file_path)
