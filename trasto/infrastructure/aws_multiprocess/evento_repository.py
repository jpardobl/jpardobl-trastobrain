
import json

from trasto.infrastructure.aws_multiprocess.aws import (EVENTOS_QUEUE_NAME,
                                                        get_queue)
from trasto.infrastructure.memory.repositories import Idefier, LoggerRepository
from trasto.model.events import (AccionTerminada, EstadoHumorCambiado,
                                 EventRepositoryInterface, NuevaAccionCreada, Evento)


MESSAGE_GROUP_ID = "1"
MAX_NUMBER_OF_MESSAGES = 1
POLL_TIME = 10

class EventoRepository(EventRepositoryInterface):
    def __init__(self):
        self.logger = LoggerRepository('comando_repo')
        self.eventos = get_queue(EVENTOS_QUEUE_NAME)


    @staticmethod
    def to_json(evento: Evento):
        if isinstance(evento, AccionTerminada):
            return {
                "clase": "AccionTerminada",
                "idd": evento.idd,
                "accion_idd": evento.accion_idd,
                "tarea_idd": evento.tarea_idd
            }

    @staticmethod
    def from_json(evento: dict):
        if evento['clase'] == 'AccionTerminada':
            return AccionTerminada(**evento)

        if evento['clase'] == 'EstadoHumorCambiado':
            return EstadoHumorCambiado(**evento)
        
        if evento['clase'] == 'NuevaAccionCreada':
            return NuevaAccionCreada(**evento)

    @staticmethod
    def serialize(evento: dict):
        return json.dumps(EventoRepository.to_json(evento))


    @staticmethod
    def deserialize(evento:str):
        return EventoRepository.from_json(json.loads(evento))


    def pub_event(self, evento: Evento):
        try:

            self.eventos.send_message(
                MessageBody=EventoRepository.serialize(evento),
                MessageGroupId=MESSAGE_GROUP_ID,
                MessageDeduplicationId=str(evento.idd))
            self.logger.debug("Evento enviado")
            return True
        except Exception:
            return False


    def subscribe_event(self):
        while True:
            try:            
                self.logger.debug("Esperando por eventos")
                msg = self.eventos.receive_messages(
                    MaxNumberOfMessages=MAX_NUMBER_OF_MESSAGES,
                    WaitTimeSeconds=POLL_TIME,
                    AttributeNames=['MessageDeduplicationId', 'MessageGroupId']
                )
                self.logger.debug("Han llegado eventos")
                for cc in msg:
                    yield EventoRepository.deserialize(cc), msg
 
            except Exception as ex:
                self.logger.error(ex)
                continue
