import json
from queue import Empty, Full, PriorityQueue, Queue

from trasto.infrastructure.aws_multiprocess.accion_repository import \
    AccionRepository
from trasto.infrastructure.aws_multiprocess.aws import get_queue, COMANDOS_QUEUE_NAME
from trasto.infrastructure.memory.repositories import Idefier, LoggerRepository
from trasto.model.commands import (Comando, ComandoNuevaAccion,
                                   ComandoNuevaTarea,
                                   ComandoRepositoryInterface)
from trasto.model.entities import (Accion, AccionRepositoryInterface,
                                   Prioridad, Tarea, TareaRepositoryInterface)
from trasto.model.events import EventRepositoryInterface, Evento
from trasto.model.value_entities import Idd, ResultadoAccion, TipoAccion


MESSAGE_GROUP_ID = "1"
MAX_NUMBER_OF_MESSAGES = 1
POLL_TIME = 10




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
            idd=tarea['idd'],
            accionid=tarea['accionid'],
            parametros=tarea['parametros'],
            nombre=tarea['nombre'],
            prioridad=tarea['prioridad']
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
        self.comandos = get_queue(COMANDOS_QUEUE_NAME)

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

                cmd = self.comandos.receive_messages(
                    MaxNumberOfMessages=MAX_NUMBER_OF_MESSAGES,
                    WaitTimeSeconds=POLL_TIME,
                    AttributeNames=['MessageDeduplicationId', 'MessageGroupId']
                )
                for cc in cmd:
                    c = json.loads(cc.body)
                    
                    if c['clase'] == "ComandoNuevaTarea":
                        yield (ComandoRepository.deserialize_comando_nueva_tarea(c), cc)
                    if c['clase'] == "ComandoNuevaAccion":
                        yield (ComandoRepository.deserialize_comando_nueva_accion(c), cc)
            except Empty:
                pass


    def send_comando(self, comando):
        self.comandos.send_message(
            MessageBody=ComandoRepository.serialize(comando),
            MessageGroupId=MESSAGE_GROUP_ID,
            MessageDeduplicationId=str(comando.idd))
        self.logger.debug("Comando enviado")
