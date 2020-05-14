
import json

from trasto.infrastructure.awsmultiprocess.aws import (EVENTOS_QUEUE_NAME,
                                                        get_queue)
from trasto.infrastructure.memory.repositories import Idefier, LoggerRepository
from trasto.model.events import (AccionTerminada, EstadoHumorCambiado,
                                 EventRepositoryInterface, NuevaAccionCreada, Evento)


MESSAGE_GROUP_ID = "1"
MAX_NUMBER_OF_MESSAGES = 1
POLL_TIME = 5

class EventoNotImplemented(Exception):
    pass


class EventoRepository(EventRepositoryInterface):
    def __init__(self):
        self.logger = LoggerRepository('evento_repo')
        self.eventos = get_queue(EVENTOS_QUEUE_NAME)


    @staticmethod
    def to_json(evento: Evento):
        if isinstance(evento, AccionTerminada):
            return {
                "clase": "AccionTerminada",
                "idd": str(evento.idd),
                "tarea_idd": str(evento.tarea_idd),
                "resultado": {
                    "codigo": str(evento.resultado.codigo),
                    "msg": evento.resultado.msg
                }
            }
        if isinstance(evento, NuevaAccionCreada):
            return {
                "clase": "NuevaAccionCreada",
                "idd": str(evento.idd),
                "accion_idd": str(evento.accion_idd),
                "accion_nombre": str(evento.accion_nombre)
            }
        if isinstance(evento, EstadoHumorCambiado):
            return {
                "clase": "EstadoHumorCambiado",
                "idd": str(evento.idd),
                "nuevo_estado_humor": evento.nuevo_estado_humor
            }
        raise EventoNotImplemented(evento)
        

    @staticmethod
    def from_json(evento: dict):
        if evento['clase'] == 'AccionTerminada':
            evento.pop('clase')
            return AccionTerminada(**evento)

        if evento['clase'] == 'EstadoHumorCambiado':
            evento.pop('clase')
            return EstadoHumorCambiado(**evento)
        
        if evento['clase'] == 'NuevaAccionCreada':
            evento.pop('clase')
            return NuevaAccionCreada(**evento)

    @staticmethod
    def serialize(evento: dict):
        return json.dumps(EventoRepository.to_json(evento))


    @staticmethod
    def deserialize(evento:str):
        return EventoRepository.from_json(json.loads(evento))


    def pub_event(self, evento: Evento):
        try:
            evs = EventoRepository.serialize(evento)
            self.logger.debug(f"Intentado enviar el evento: {evs}")
            
            self.eventos.send_message(
                MessageBody=evs,
                MessageGroupId=MESSAGE_GROUP_ID,
                MessageDeduplicationId=str(evento.idd))
            self.logger.debug("Evento enviado")
            return True
        
        except EventoNotImplemented as exx:
            raise exx

        except Exception as ex:
            self.logger.error(f"Sending event: {ex}")
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
                #self.logger.debug(f"Han llegado eventos: {msg}")
                for cc in msg:
                    if cc is None:
                        break
                    c = json.loads(cc.body)
                    cc.delete()
                    yield EventoRepository.from_json(c)
 
            except Exception as ex:
                self.logger.error(ex)
                continue
