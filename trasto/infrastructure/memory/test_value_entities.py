import pytest


from trasto.model.value_entities import *
from trasto.infrastructure.memory.repositories import Idefier


def test_idd():
    idd1 = Idd(Idefier())
    idd2 = Idd(Idefier())
    assert isinstance(idd1.id, str)
    assert idd1 == idd1
    assert idd2 != idd1
    assert idd1 != idd2

    idd3 = Idd(Idefier(), idd_str=idd1.id)
    assert idd1 == idd3
    assert idd3 == idd1

    