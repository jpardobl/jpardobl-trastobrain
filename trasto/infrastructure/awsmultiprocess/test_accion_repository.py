
import pytest
from trasto.infrastructure import AccionNotFoundError
from trasto.infrastructure.awsmultiprocess.accion_repository import (AccionRepository)
from trasto.infrastructure.awsmultiprocess.aws import \
    create_dynamodb_acciones_table
from trasto.infrastructure.awsmultiprocess.evento_repository import \
    EventoRepository
from trasto.infrastructure.memory.repositories import Idefier
from trasto.model.entities import Accion
from trasto.model.value_entities import Idd, TipoAccion

#from trasto.infrastructure.awsmultiprocess.accion_repository import 


def test_get_by_id():

    accion_repo = AccionRepository()
    evento_repo = EventoRepository()
    accion_repo.purge_table()
    a = Accion(
        idd=Idd(Idefier()),
        nombre="nombreaccion",
        script_url="git://script_url",
        tipo=TipoAccion(nombre="buenhumor")
    )

    accion_repo.append_accion(a, evento_repo)
    a2 = Accion(
        idd=Idd(Idefier()),
        nombre="nombreaccion2",
        script_url="git://script_url2",
        tipo=TipoAccion(nombre="malhumor")
    )
    
    with pytest.raises(AccionNotFoundError): 
        acc = accion_repo.get_accion_by_id(a2.idd)

    acc = accion_repo.get_accion_by_id(a.idd)
    assert acc.idd == a.idd
    assert acc.tipo == a.tipo



def test_get_by_tipo():
    accion_repo = AccionRepository()
    evento_repo = EventoRepository()

    accion_repo.purge_table()
    a = Accion(
        idd=Idd(Idefier()),
        nombre="accion_buen_humor",
        script_url="git://script_url",
        tipo=TipoAccion(nombre="buenhumor")
    )
    a1 = Accion(
        idd=Idd(Idefier()),
        nombre="accion_buen_humor1",
        script_url="git://script_url",
        tipo=TipoAccion(nombre="buenhumor")
    )
    
    a2 = Accion(
        idd=Idd(Idefier()),
        nombre="accion_mal_humor",
        script_url="git://script_url",
        tipo=TipoAccion(nombre="malhumor")
    )
    accion_repo.append_accion(a, evento_repo)
    accion_repo.append_accion(a1, evento_repo)
    accion_repo.append_accion(a2, evento_repo)

    count = 0
    for acc in accion_repo.get_acciones_by_type(TipoAccion(nombre="buenhumor")):
        assert isinstance(acc, Accion)
        assert acc.tipo == TipoAccion(nombre="buenhumor")
        count = count + 1

    assert count == 2


def test_get_all():
    accion_repo = AccionRepository()
    evento_repo = EventoRepository()

    accion_repo.purge_table()
    a = Accion(
        idd=Idd(Idefier()),
        nombre="accion_buen_humor",
        script_url="git://script_url",
        tipo=TipoAccion(nombre="buenhumor")
    )
    a1 = Accion(
        idd=Idd(Idefier()),
        nombre="accion_buen_humor1",
        script_url="git://script_url",
        tipo=TipoAccion(nombre="buenhumor")
    )
    
    a2 = Accion(
        idd=Idd(Idefier()),
        nombre="accion_mal_humor",
        script_url="git://script_url",
        tipo=TipoAccion(nombre="malhumor")
    )
    accion_repo.append_accion(a, evento_repo)
    accion_repo.append_accion(a1, evento_repo)
    accion_repo.append_accion(a2, evento_repo)

    count = 0
    for acc in accion_repo.get_all_json():
        assert isinstance(acc, dict)
        count = count + 1
    assert count == 3