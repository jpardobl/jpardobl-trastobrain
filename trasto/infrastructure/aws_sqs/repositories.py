import json
from queue import Empty, Full, PriorityQueue, Queue

from trasto.infrastructure.memory.repositories import LoggerRepository,Idefier
from trasto.model.commands import ComandoRepositoryInterface, Comando, ComandoNuevaAccion, ComandoNuevaTarea
from trasto.model.entities import (Accion, AccionRepositoryInterface,
                                   Prioridad, Tarea, TareaRepositoryInterface)
from trasto.model.events import EventRepositoryInterface
from trasto.model.value_entities import Idd, ResultadoAccion, TipoAccion
from trasto.infrastructure.aws_sqs.aws import get_aws_session, create_or_get_fifo_queue, AWS_PROFILE

TAREAS_NORMALES_QUEUE_NAME = "trastobrain_tareas_normales"
TAREAS_PRIORITARIAS_QUEUE_NAME = "trastobrain_tareas_prioritarias"
COMANDOS_QUEUE_NAME = "trastobrain_comandos"
EVENTOS_QUEUE_NAME = "trastobrain_eventos"

tareas_normales = create_or_get_fifo_queue(TAREAS_NORMALES_QUEUE_NAME, get_aws_session(profile_name=AWS_PROFILE))
tareas_prioritarias = create_or_get_fifo_queue(TAREAS_PRIORITARIAS_QUEUE_NAME, get_aws_session(profile_name=AWS_PROFILE))
comandos = create_or_get_fifo_queue(COMANDOS_QUEUE_NAME, get_aws_session(profile_name=AWS_PROFILE))
eventos = create_or_get_fifo_queue(EVENTOS_QUEUE_NAME, get_aws_session(profile_name=AWS_PROFILE))

MESSAGE_GROUP_ID = "1"
MAX_NUMBER_OF_MESSAGES = 1
POLL_TIME = 10

class AccionNotFoundException(Exception):
    pass


class EventoRepository(EventRepositoryInterface):
    def __init__(self):
        self.logger = LoggerRepository('comando_repo')

    def pub_event(self, evento):
        try:
            eventos.put(evento)
            return True
        except Exception:
            return False

    def subscribe_event(self):
        while True:
            try:
                yield eventos.get(block=True, timeout=QUEUE_TIMEOUT)
            except Exception as ex:
                self.logger.error(ex)
                continue
                

class TareaRepository(TareaRepositoryInterface):

    def __init__(self):
        self.logger = LoggerRepository('tarea_repo')

    @staticmethod
    def to_json(tarea: Tarea) -> dict:
        return {
            "idd": str(tarea.idd),
            "accionid": tarea.accionid,
            "parametros": tarea.parametros,
            "nombre": tarea.nombre,
            "prioridad": tarea.prioridad
        }

    @staticmethod
    def serialize(tarea: Tarea) -> str:
        return json.dumps(TareaRepository.serialize(tarea))

    @staticmethod
    def deserialize(tarea: dict) ->Tarea:
        return Tarea(
            idd=tarea.idd,
            accionid=tarea.accionid,
            parametros=tarea.parametros,
            nombre=tarea.nombre,
            prioridad=tarea.prioridad
        )


    def next_tarea(self):
        while True:
            try:
                self.logger.debug("esperando por tarea")
                yield tareas.get(block=True, timeout=QUEUE_TIMEOUT)
            except Empty:
                pass


    def append(self, tarea: Tarea):
        try:
            tareas.put(tarea)
        except:
            self.logger.crit("Cola de tareas llena!!!!")


class ComandoRepository(ComandoRepositoryInterface):
    def __init__(self):
        self.logger = LoggerRepository('comando_repo')

    @staticmethod
    def serialize(comando: Comando) -> str:
        if isinstance(comando, ComandoNuevaTarea):
            return json.dumps({
                "clase": "ComandoNuevaTarea",
                "idd": str(comando.idd),
                "tarea": TareaRepository.to_json(comando.tarea)
            })
        if isinstance(comando, ComandoNuevaAccion):
            return json.dumps({
                "clase": "ComandoNuevaAccion",
                "idd": str(comando.idd),
                "accion": AccionRepository.to_json(accion=comando.accion)
            })

    @staticmethod
    def deserialize_comando_nueva_tarea(comando: dict) -> ComandoNuevaTarea:
        return ComandoNuevaTarea(
            idd=Idd(Idefier(), idd_str=comando['idd']),
            tarea=TareaRepository.deserialize(comando['tarea'])
        )

    @staticmethod
    def deserialize_comando_nueva_accion(comando: dict) -> ComandoNuevaAccion:
        return ComandoNuevaAccion(
            idd=Idd(Idefier(), idd_str=comando['idd']),
            accion=AccionRepository.deserialize(comando['accion'])
        )

    def next_comando(self):
        while True:
            try:
                self.logger.debug("Esperamos por nuevo comando")

                cmd = comandos.receive_messages(
                    MaxNumberOfMessages=MAX_NUMBER_OF_MESSAGES,
                    WaitTimeSeconds=POLL_TIME,
                    AttributeNames=['MessageDeduplicationId', 'MessageGroupId']
                )
                for cc in cmd:
                    c = json.loads(cc.body)
                    print(c)
                    if c['clase'] == "ComandoNuevaTarea":
                        yield (ComandoRepository.deserialize_comando_nueva_tarea(c), cc)
                    if c['clase'] == "ComandoNuevaAccion":
                        yield (ComandoRepository.deserialize_comando_nueva_accion(c), cc)
            except Empty:
                pass


    def send_comando(self, comando):
        comandos.send_message(
            MessageBody=ComandoRepository.serialize(comando),
            MessageGroupId=MESSAGE_GROUP_ID,
            MessageDeduplicationId=str(comando.idd))
        self.logger.debug("Comando enviado")


class AccionRepository(AccionRepositoryInterface):
    def __init__(self):
        self.logger = LoggerRepository('accion_repo')
        self.acciones = list()

    @staticmethod
    def to_json(accion: Accion) -> dict:
        return {
            "idd": str(accion.idd),
            "nombre": accion.nombre,
            "script_url": accion.script_url,
            "tipo": str(accion.tipo)
        }

    @staticmethod
    def serialize(accion: Accion) -> str:
        return json.dumps(AccionRepository.to_json(accion))

    @staticmethod
    def deserialize(accion: dict) -> Accion:
        return Accion(
            idd=accion['idd'],
            nombre=accion['nombre'],
            script_url=accion['script_url'],
            tipo=accion['tipo']
        )

    def get_actiones_by_type(self, tipo: TipoAccion):
        for accion in self.acciones:
            if accion.tipo == tipo:
                yield accion

    def get_all(self):
        return tuple(a for a in self.acciones)


    def get_acciones_by_id(self, idd: Idd):
        self.logger.debug(f"Buscamos accion con la idd: {idd}")
        for accion in self.acciones:
            self.logger.debug(f"Miramos si esta accion {accion} corresponde con id: {idd}")
            if accion.idd == idd:
                return accion
        raise AccionNotFoundException(f"idd={idd}")

    def get_acciones_buen_humor(self):
        return (a for a in self.get_acciones_by_type(TipoAccion(TipoAccion.BUEN_HUMOR)))
    
    def get_acciones_mal_humor(self):
        return (a for a in self.get_acciones_by_type(TipoAccion(TipoAccion.MAL_HUMOR)))

    def del_accion(self, accion: Accion):
        self.acciones.remove(accion)
            
    def rollback_append_accion(self, accion: Accion):
        self.logger.debug("Rolling back append accion")
        self.del_accion(accion)

    def append_accion(self, accion: Accion, evento_repo: EventRepositoryInterface):
        try:
            self.logger.debug("Apending nueva accion")
            self.acciones.append(accion)
            emitido = evento_repo.pub_event(accion)
            if not emitido:
                self.rollback_append_accion(accion=accion)
        except Exception as ex:
            self.logger.error(ex)
            self.rollback_append_accion(accion=accion)


    def get_all_json(self):
        return tuple(json.loads(AccionRepository.to_json(accion)) for accion in self.get_all())
