
from trasto.infrastructure.awsmultiprocess.comando_repository import (
    COMANDOS_QUEUE_NAME, ComandoRepository)
from trasto.infrastructure.memory.repositories import Idefier
from trasto.model.commands import (Comando, ComandoNuevaAccion,
                                   ComandoNuevaTarea)
from trasto.model.entities import Accion, Tarea
from trasto.model.value_entities import Idd, TipoAccion


def test_comando_nueva_accion():
    comando_repo = ComandoRepository()

    cna = ComandoNuevaAccion(
        idd=Idd(Idefier()),
        accion=Accion(
            idd=Idd(Idefier()),
            nombre="nombreaccion",
            script_url="url",
            tipo=TipoAccion(nombre="buenhumor")
        )
    )

    comando_repo.send_comando(cna)
    count = 0
    for ccna in comando_repo.next_comando():
        assert not ccna is None
        assert isinstance(ccna, ComandoNuevaAccion)
        assert ccna.accion.nombre == "nombreaccion"
        count = count + 1
        break
    assert count == 1



def test_comando_nueva_tarea():

    comando_repo = ComandoRepository()
    cnt_alta = ComandoNuevaTarea(
        idd=Idd(Idefier()),
        tarea=Tarea(
            idd=Idd(Idefier()),
            nombre="Tareaalta",
            parametros="parametros",
            prioridad=1,
            accionid="accion"
        )
    )

    cnt_baja = ComandoNuevaTarea(
        idd=Idd(Idefier()),
        tarea=Tarea(
            idd=Idd(Idefier()),
            nombre="Tareabaja",
            parametros="parametros",
            prioridad=0,
            accionid="accion"
        )
    )
    comando_repo.send_comando(cnt_alta)
    comando_repo.send_comando(cnt_baja)

    count = 0
    for ccnt in comando_repo.next_comando():
        assert isinstance(ccnt, ComandoNuevaTarea)
        assert ccnt.tarea.nombre in ("Tareabaja", "Tareaalta")
        print(f"vamos por contador: {count}")
        count = count + 1
        if count == 2:
            break
    assert count == 2