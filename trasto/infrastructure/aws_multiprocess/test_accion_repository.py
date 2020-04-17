

from trasto.infrastructure.aws_multiprocess.repositories import AccionRepository, EventoRepository
from trasto.model.entities import Accion
from trasto.model.value_entities import Idd, TipoAccion
from trasto.infrastructure.memory.repositories import Idefier

from trasto.infrastructure.aws_multiprocess.aws import create_dynamodb_acciones_table
from trasto.infrastructure.aws_multiprocess.accion_repository import TABLE_NAME

def test_get_by_id():

    accion_repo = AccionRepository()
    evento_repo = EventoRepository()

    a = Accion(
        idd=Idd(Idefier()),
        nombre="nombreaccion",
        script_url="git://script_url",
        tipo=TipoAccion(nombre="buenhumor")
    )

    accion_repo.append_accion(a, evento_repo)

    acc = accion_repo.get_accion_by_id(a.idd)
    assert acc.idd == a.idda
    assert acc.tipo == a.tipo


def test_get_by_tipo():
    accion_repo = AccionRepository()
    evento_repo = EventoRepository()

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
    for acc in accion_repo.get_actiones_by_type(TipoAccion(nombre="buenhumor")):
        assert isinstance(acc, Accion)
        assert acc.tipo == "buenhumor"
        count = count + 1

    assert count == 2

    delete_table(TABLE_NAME)

def test_get_by_idd():

    accion_repo = AccionRepository()
    evento_repo = EventoRepository()

    a = Accion(
        idd=Idd(Idefier()),
        nombre="accion_buen_humor",
        script_url="git://script_url",
        tipo=TipoAccion(nombre="buenhumor")
    )
    accion_repo.append_accion(a, evento_repo)

    acc = accion_repo.get_accion_by_id(a.idd)

    assert acc.idd == a.idd
    
        

