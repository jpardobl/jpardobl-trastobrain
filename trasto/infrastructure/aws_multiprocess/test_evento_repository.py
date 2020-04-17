

from trasto.infrastructure.aws_multiprocess.evento_repository import \
    EventoRepository
from trasto.infrastructure.memory.repositories import Idefier
from trasto.model.events import (AccionTerminada, EstadoHumorCambiado,
                                 NuevaAccionCreada)
from trasto.model.value_entities import Idd, ResultadoAccion, CodigoResultado


def test_evento_accion_terminada():
    evento_repo = EventoRepository()

    evento = AccionTerminada(
        idd=Idd(Idefier()),
        tarea_idd=Idd(Idefier()),
        resultado=ResultadoAccion(
            codigo=CodigoResultado(codigo="BIEN")
        )
    )

    evento_repo.pub_event(evento=evento)

    
    for ev, msg in evento_repo.subscribe_event():
        assert ev.idd == evento.idd
        assert ev.tarea_idd == evento.idd
        assert ev.resultado.codigo == "BIEN"
        msg.delete()
        break


def test_evento_estado_humor_cambiado():

    evento_repo = EventoRepository()

    evento = EstadoHumorCambiado(
        idd=Idd(Idefier()),
        nuevo_estado_humor=300
    )

    evento_repo.pub_event(evento=evento)

    for ev, msg in evento_repo.subscribe_event():
        assert ev.idd == evento.idd
        assert ev.nuevo_estado_humor == 300
        msg.delete()
        break

    
def test_evento_nueva_accion_creada():
    evento_repo = EventoRepository()

    evento = NuevaAccionCreada(
        idd=Idd(Idefier()),
        accion_idd=Idd(Idefier())
    )

    evento_repo.pub_event(evento)

    for ev, msg in evento_repo.subscribe_event():
        assert ev.idd == evento.idd
        assert ev.accion_idd == evento.accion_idd
        msg.delete()
        break
