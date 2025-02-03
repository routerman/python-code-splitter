from pathlib import Path

import pytest

from src.services.load_file_service import LoadFileService


def test_load_file_service():
    service = LoadFileService(file_path=Path("tests/samples/models.py"))
    result = service.execute()
    from pprint import pprint

    pprint(result)
    block_names = [block.name for block in result.blocks]
    assert "KlassWithMember" in block_names
    assert "KlassWithFunction" in block_names
    assert "KlassWithMetaKlass" in block_names
    assert "KlassWithComment1" in block_names
    assert "KlassWithComment2" in block_names
    assert "KlassWithDecorator" in block_names
    assert "function_with_comment1" in block_names
    raise


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
