from ament_pep257.main import main
import pytest


@pytest.mark.linter
@pytest.mark.pep257
def testPep257():
    result = main(argv=['.', 'test'])
    assert result == 0, 'Found code style errors / warnings'
