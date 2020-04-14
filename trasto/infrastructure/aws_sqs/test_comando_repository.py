from trasto.infrastructure.aws_sqs.repositories import ComandoRepository, COMANDOS_QUEUE_NAME
from trasto.model.commands import Comando, ComandoNuevaAccion, ComandoNuevaTarea
from trasto.model.value_entities import Idd, TipoAccion
from trasto.model.entities import Accion, Tarea
from trasto.infrastructure.memory.repositories import Idefier
from trasto.infrastructure.aws_sqs.aws import delete_queue, get_aws_session, AWS_PROFILE

def off_test_comando_nueva_accion():


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
    for ccna, msg in comando_repo.next_comando():
        assert not ccna is None
        assert isinstance(ccna, ComandoNuevaAccion)
        assert ccna.accion.nombre == "nombreaccion"
        msg.delete()
        break

    delete_queue(COMANDOS_QUEUE_NAME, get_aws_session(profile_name=AWS_PROFILE))


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

    comando_repo.send_comando(cnt_alta)
    comando_repo.send_comando(cnt_baja)

    count = 0
    for ccnt in comando_repo.next_comando():
        assert isinstance(ccnt, ComandoNuevaTarea)
        assert ccnt.tarea.nombre in ("tareabaja", "tareaalta")
        count = count + 1
        if count == 2:
            break

    delete_queue(COMANDOS_QUEUE_NAME, get_aws_session(profile_name=AWS_PROFILE))