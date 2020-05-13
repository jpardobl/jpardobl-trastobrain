import json
#from queue import Empty, Full, PriorityQueue, Queue
from trasto.infrastructure.awsmultiprocess.tarea_repository import TareaRepository
from trasto.infrastructure.awsmultiprocess.accion_repository import AccionRepository
from trasto.infrastructure.awsmultiprocess.aws import get_queue, COMANDOS_QUEUE_NAME
from trasto.infrastructure.memory.repositories import Idefier, LoggerRepository
from trasto.model.commands import (Comando, ComandoNuevaAccion,
                                   ComandoNuevaTarea,
                                   ComandoRepositoryInterface)
from trasto.model.entities import (AccionRepositoryInterface,
                                   Prioridad, Tarea, TareaRepositoryInterface)
from trasto.model.events import EventRepositoryInterface, Evento
from trasto.model.value_entities import Idd, ResultadoAccion, TipoAccion


MESSAGE_GROUP_ID = "1"
MAX_NUMBER_OF_MESSAGES = 1
POLL_TIME = 10


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
            self.logger.debug("Esperamos por nuevo comando")
            cmd = self.comandos.receive_messages(
                MaxNumberOfMessages=MAX_NUMBER_OF_MESSAGES,
                WaitTimeSeconds=POLL_TIME,
                AttributeNames=['MessageDeduplicationId', 'MessageGroupId']
            )

            for cc in cmd:
                c = json.loads(cc.body)
                cc.delete()
                if c['clase'] == "ComandoNuevaTarea":
                    yield ComandoRepository.deserialize_comando_nueva_tarea(c)
                if c['clase'] == "ComandoNuevaAccion":
                    yield ComandoRepository.deserialize_comando_nueva_accion(c)





    def send_comando(self, comando):
        try:
            self.logger.debug(f"Intentamos enviar el comando::: {comando}")
            response = self.comandos.send_message(
                MessageBody=ComandoRepository.serialize(comando),
                MessageGroupId=MESSAGE_GROUP_ID,
                MessageDeduplicationId=str(comando.idd))
            
            self.logger.debug(f"Comando enviado: [{comando}], messageid: [{response['MessageId']}]")
        except Exception as ex:
            self.logger.error(f"Error intentando enviar un comando: {ex}")
