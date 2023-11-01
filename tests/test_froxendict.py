import pytest
from PyCustomCollections.CustomDataStructures import FrozenDict


def test_frozendict_readonly():
    fd = FrozenDict({'Test': "readonly"})
    with pytest.raises(TypeError):
        fd.update({'Tets': "I wanna be changed"})