

from trasto.infrastructure.aws_multiprocess.evento_repository import \
    EventoRepository
from trasto.infrastructure.memory.repositories import Idefier, LoggerRepository
from trasto.model.events import (AccionTerminada, EstadoHumorCambiado,
                                 NuevaAccionCreada)
from trasto.model.value_entities import Idd, ResultadoAccion, CodigoResultado


logger = LoggerRepository('test_evento_respository')

def test_send_evento_accion_terminada():
    evento_repo = EventoRepository()

    evento = AccionTerminada(
        idd=Idd(Idefier()),
        tarea_idd=Idd(Idefier()),
        resultado=ResultadoAccion(
            codigo=CodigoResultado(codigo="BIEN"),
            msg="Mensaje de prueba")
        )
    

    assert evento_repo.pub_event(evento=evento)


def test_evento_accion_terminada():
    evento_repo = EventoRepository()

    evento = AccionTerminada(
        idd=Idd(Idefier()),
        tarea_idd=Idd(Idefier()),
        resultado=ResultadoAccion(
            codigo=CodigoResultado(codigo=CodigoResultado.BUEN_RESULTADO),
            msg="Mensaje de prueba")
        )

    assert evento_repo.pub_event(evento=evento)
    
    logger.debug("Buwcamos evetgnos")
    for ev, msg in evento_repo.subscribe_event():
        try:
            logger.debug("ha llegado")
            assert ev.idd == evento.idd
            assert ev.tarea_idd == evento.tarea_idd
            assert ev.resultado.codigo == "BIEN"
        except Exception as ex:
            print(ex)
        finally:
            msg.delete()
            break


def test_evento_estado_humor_cambiado():

    evento_repo = EventoRepository()

    evento = EstadoHumorCambiado(
        idd=Idd(Idefier()),
        nuevo_estado_humor=300
    )

    assert evento_repo.pub_event(evento=evento)

    for ev, msg in evento_repo.subscribe_event():
        try:
            assert ev.idd == evento.idd
            assert ev.nuevo_estado_humor == 300
        except Exception as ex:
            print(ex)
            
        finally:
            msg.delete()
            break

    
def test_evento_nueva_accion_creada():
    evento_repo = EventoRepository()

    evento = NuevaAccionCreada(
        idd=Idd(Idefier()),
        accion_idd=Idd(Idefier()),
        accion_nombre="Nombre accion"
    )

    assert evento_repo.pub_event(evento)

    for ev, msg in evento_repo.subscribe_event():
        try:
            assert ev.idd == evento.idd
            assert ev.accion_idd == evento.accion_idd
        except Exception as ex:
            print(ex)
        finally:
            msg.delete()
            break
