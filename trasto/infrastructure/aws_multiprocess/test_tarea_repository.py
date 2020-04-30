
from trasto.infrastructure.aws_multiprocess.tarea_repository import (
    TareaRepository)
#from trasto.infrastructure.aws_multiprocess.aws import TABLE_ACCIONES_NAME
from trasto.infrastructure.memory.repositories import Idefier
from trasto.model.commands import (Comando, ComandoNuevaAccion,
                                   ComandoNuevaTarea)
from trasto.model.entities import Accion, Tarea
from trasto.model.value_entities import Idd, TipoAccion


def test_enviar_recibir():
    tarea_repo = TareaRepository()
    tarea_repo.purge_queue()
    task_baja = Tarea(
        idd=Idd(Idefier()),
        nombre="tarea_baja",
        accionid="accion_id",
        parametros={"param1": "hola"},
        prioridad=0
    )
    task_alta = Tarea(
        idd=Idd(Idefier()),
        nombre="tarea_alta",
        accionid="accion_id",
        parametros={"param1": "hola"},
        prioridad=1
    )

    tarea_repo.append(task_baja)
    tarea_repo.append(task_alta)

    count = 0
    for taskc, msg in tarea_repo.next_tarea():
        assert not taskc is None
        assert isinstance(taskc, Tarea)
        assert taskc.nombre == task_alta.nombre
        assert taskc.prioridad == task_alta.prioridad
        msg.delete()
        count = count + 1
        break
    assert count == 1

    for taskc, msg in tarea_repo.next_tarea():
        assert not taskc is None
        assert isinstance(taskc, Tarea)
        assert taskc.nombre == task_baja.nombre
        assert taskc.prioridad == task_baja.prioridad
        msg.delete()
        count = count + 1
        break
    assert count == 2

