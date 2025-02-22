from pathlib import Path

import pytest

from src.entities.block import Block
from src.services.load_file_service import LoadFileService


def test_load_file_service():
    service = LoadFileService(file_path=Path("tests/samples/models.py"))
    result = service.execute()
    assert result.path == Path("tests/samples/models.py")
    assert result.blocks[0] == Block(
        type="import",
        name="other",
        codes=[
            "# This is a sample file for testing.\n",
            '"""\n',
            "This is a sample file for testing.\n",
            '"""\n',
            "\n",
            "import sys\n",
        ],
    )
    assert result.blocks[1] == Block(type="import", name="other", codes=["from dataclasses import dataclass\n"])
    assert result.blocks[2] == Block(
        type="import", name="other", codes=["from typing import (\n", "    Callable\n", ")\n"]
    )
    assert result.blocks[3] == Block(type="import", name="other", codes=["from pathlib import Path\n"])
    assert result.blocks[4] == Block(type="value", name="StrAlias", codes=["\n", "StrAlias = str\n"])
    assert result.blocks[5] == Block(
        type="value",
        name="FunctionAlias",
        codes=["# This is very important value\n", "FunctionAlias = Callable[[], None]\n"],
    )
    assert result.blocks[6] == Block(
        type="class",
        name="KlassWithMetaKlass",
        codes=["\n", "\n", "class KlassWithMetaKlass:\n", "    class Meta:\n", "        abstract = True\n"],
    )
    assert result.blocks[7] == Block(
        type="class",
        name="_KlassNameStartWithUnderScore",
        codes=["\n", "\n", "class _KlassNameStartWithUnderScore:\n", "    pass\n"],
    )
    assert result.blocks[8] == Block(
        type="class",
        name="KlassWithComment1",
        codes=[
            "\n",
            "\n",
            '"""\n',
            " - Do not delete this comment.\n",
            '"""\n',
            "\n",
            "\n",
            "class KlassWithComment1:\n",
            "    pass\n",
        ],
    )
    assert result.blocks[9] == Block(
        type="class",
        name="KlassWithComment2",
        codes=[
            "\n",
            "\n",
            "'''\n",
            '"""\n',
            " - Do not delete this comment.\n",
            "'''\n",
            "\n",
            "\n",
            "class KlassWithComment2:\n",
            "    pass\n",
        ],
    )
    assert result.blocks[10] == Block(
        type="class",
        name="KlassWithComment3",
        codes=[
            "\n",
            "\n",
            "# This is very important comment for KlassWithComment3\n",
            "# This is sample class\n",
            "class KlassWithComment3:\n",
            "    pass\n",
        ],
    )
    assert result.blocks[11] == Block(
        type="class",
        name="KlassWithDecorator",
        codes=["\n", "\n", "@dataclass(frozen=True)\n", "class KlassWithDecorator:\n", "    pass\n"],
    )
    assert result.blocks[12] == Block(
        type="class",
        name="KlassWithCommentAndDecorator",
        codes=[
            "\n",
            "\n",
            '"""\n',
            "    class with comment and decorator\n",
            "from this import is dummy\n",
            "def this_is_comment():\n",
            "    pass\n",
            '"""\n',
            "\n",
            "\n",
            "@dataclass(frozen=True)\n",
            "class KlassWithCommentAndDecorator:\n",
            "    pass\n",
        ],
    )
    assert result.blocks[13] == Block(
        type="value", name="class_value1", codes=["\n", "\n", 'class_value1 = "default1"\n']
    )
    assert result.blocks[14] == Block(type="value", name="class_value2", codes=['class_value2 = "default2"\n'])
    assert result.blocks[15] == Block(
        type="class",
        name="KlassWithMember",
        codes=[
            "\n",
            "\n",
            "class KlassWithMember:\n",
            "    value: StrAlias\n",
            "    meta: KlassWithMetaKlass\n",
        ],
    )
    assert result.blocks[16] == Block(
        type="class",
        name="KlassWithFunction",
        codes=[
            "\n",
            "\n",
            "class KlassWithFunction(KlassWithComment1):\n",
            "    def hoge(self):\n",
            "        pass\n",
        ],
    )
    assert result.blocks[17] == Block(
        type="function",
        name="_function_start_with_underscore",
        codes=[
            "\n",
            "\n",
            'if __name__ == "__main__":\n',
            '    print("Hello, World!")\n',
            "    sys.exit(0)\n",
            "\n",
            "\n",
            "def _function_start_with_underscore(klass: KlassWithComment2):\n",
            "    print(klass)\n",
        ],
    )
    assert result.blocks[18] == Block(
        type="function",
        name="function_with_comment1",
        codes=[
            "\n",
            "\n",
            '"""\n',
            "- Do not delete this comment for function_with_comment1\n",
            '"""\n',
            "\n",
            "\n",
            "def function_with_comment1(path: Path):\n",
            "    pass\n",
        ],
    )
    assert result.blocks[19] == Block(
        type="function",
        name="function_with_comment2",
        codes=[
            "\n",
            "\n",
            "'''\n",
            '"""\n',
            "    - Do not delete this comment for function_with_comment2\n",
            "'''\n",
            "\n",
            "\n",
            "def function_with_comment2():\n",
            "    pass\n",
        ],
    )
    assert result.blocks[20] == Block(
        type="function",
        name="function_with_comment3",
        codes=[
            "\n",
            "\n",
            "# This is very important comment for function_with_comment3\n",
            "# This is sample class\n",
            "def function_with_comment3():\n",
            "    pass\n",
        ],
    )
    assert result.blocks[21] == Block(
        type="function",
        name="function_with_decorator",
        codes=["\n", "\n", "@staticmethod\n", "def function_with_decorator():\n", "    pass\n"],
    )
    assert result.blocks[22] == Block(type="value", name="def_value", codes=["\n", "\n", "def_value = 1\n"])
    assert result.blocks[23] == Block(
        type="function",
        name="function_with_comment_and_decorator",
        codes=[
            "\n",
            "\n",
            "# this comment for function_with_comment_and_decorator\n",
            "@staticmethod\n",
            "def function_with_comment_and_decorator():\n",
            "    pass\n",
        ],
    )
    assert result.blocks[24] == Block(
        type="function",
        name="function_with_async",
        codes=["\n", "\n", "async def function_with_async():\n", "    pass\n"],
    )
    assert result.blocks[25] == Block(type="value", name="last_value", codes=["\n", "\n", "last_value = 100\n"])


def test_load_file_service_non_existent_file():
    with pytest.raises(AssertionError):
        service = LoadFileService(file_path=Path("tests/non_existent_file.py"))
        service.execute()


def test_load_file_service_empty_file(tmp_path):
    empty_file = tmp_path / "empty.py"
    empty_file.touch()
    service = LoadFileService(file_path=empty_file)
    result = service.execute()
    assert len(result.blocks) == 0
