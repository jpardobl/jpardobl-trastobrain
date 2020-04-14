import pytest
from trasto.infrastructure.asyncio.repositories import AccionRepository, EventoRepository, AccionNotFoundException
from trasto.infrastructure.memory.repositories import Idefier
from trasto.model.value_entities import Idd
from trasto.model.entities import Accion


def test_get_all():
    idefier = Idefier()
    accion = Accion(Idd(idefier), "nombre", "script_url", "enfado")
    evento_repo = EventoRepository()
    accion_repo = AccionRepository()

    acciones = accion_repo.get_all_json()


    assert len(acciones) == 0, "Deberia mostrar ninguna accion"

    accion_repo.append_accion(accion, evento_repo)
    acciones = accion_repo.get_all_json()
    assert len(acciones) == 1, "Deberia mostrar una sola accion"

    accion_repo.append_accion(accion, evento_repo)
    acciones = accion_repo.get_all_json()
    assert len(acciones) == 2, "Deberia mostrar dos acciones"


def test_get_by_id():

    idefier = Idefier()
    accion = Accion(Idd(idefier), "nombre", "script_url", "enfado")
    evento_repo = EventoRepository()
    accion_repo = AccionRepository()

    accion_repo.append_accion(accion, evento_repo)
    acciones = accion_repo.get_all()

    #with pytest.raises(AccionNotFoundException):
    #    accion = accion_repo.get_accion_by_id(Idd(idefier, "estanoexiste"))
    print(acciones)
    id_str = acciones[0].idd

    accion = accion_repo.get_acciones_by_id(Idd(idefier, id_str))
    assert accion.idd == id_str, "Deberia haber recuperado la accion con idd igual al que creo"


