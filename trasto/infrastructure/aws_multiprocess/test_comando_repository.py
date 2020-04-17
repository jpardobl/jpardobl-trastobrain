from trasto.infrastructure.aws_multiprocess.aws import (AWS_PROFILE,
                                                        get_aws_session)
from trasto.infrastructure.aws_multiprocess.repositories import (
    COMANDOS_QUEUE_NAME, ComandoRepository)
from trasto.infrastructure.memory.repositories import Idefier
from trasto.model.commands import (Comando, ComandoNuevaAccion,
                                   ComandoNuevaTarea)
from trasto.model.entities import Accion, Tarea
from trasto.model.value_entities import Idd, TipoAccion


def test_comando_nueva_accion():
    comando_repo = ComandoRepository()
    print(comando_repo.comandos)
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
    for ccna, msg in comando_repo.next_comando():
        assert not ccna is None
        assert isinstance(ccna, ComandoNuevaAccion)
        assert ccna.accion.nombre == "nombreaccion"
        msg.delete()
        break



def test_comando_nueva_tarea():

    comando_repo = ComandoRepository()
    cnt_alta = ComandoNuevaTarea(
        idd=Idd(Idefier()),
        tarea=Tarea(
            idd=Idd(Idefier()),
            nombre="tareaalta",
            parametros="parametros",
            prioridad=1,
            accionid="accion"
        )
    )

    cnt_baja = ComandoNuevaTarea(
        idd=Idd(Idefier()),
        tarea=Tarea(
            idd=Idd(Idefier()),
            nombre="tareabaja",
            parametros="parametros",
            prioridad=0,
            accionid="accion"
        )
    )
    print(f"Enviamos: {cnt_alta}")
    comando_repo.send_comando(cnt_alta)
    comando_repo.send_comando(cnt_baja)

    count = 0
    for ccnt, msg in comando_repo.next_comando():
        assert isinstance(ccnt, ComandoNuevaTarea)
        assert ccnt.tarea.nombre in ("tareabaja", "tareaalta")
        msg.delete()
        count = count + 1
        if count == 2:
            break
