import json

from trasto.infrastructure.memory.repositories import (Idd, Idefier,
                                                       LoggerRepository)
from trasto.model.entities import Tarea, TareaRepositoryInterface
from trasto.infrastructure.awsmultiprocess.aws import get_queue, TAREAS_NORMALES_QUEUE_NAME, TAREAS_PRIORITARIAS_QUEUE_NAME
from trasto.model.value_entities import Prioridad
from trasto.infrastructure.awsmultiprocess.aws import get_sqs_client

MESSAGE_GROUP_ID = "1"
MAX_NUMBER_OF_MESSAGES = 1
POLL_TIME = 2

class TareaRepository(TareaRepositoryInterface):

    def __init__(self):
        self.logger = LoggerRepository('tarea_repo')
        self.tareas_prio = get_queue(TAREAS_PRIORITARIAS_QUEUE_NAME)
        self.tareas_norm = get_queue(TAREAS_NORMALES_QUEUE_NAME)

    def purge_queue(self):
        get_sqs_client().purge_queue(QueueUrl=self.tareas_norm.url)
        get_sqs_client().purge_queue(QueueUrl=self.tareas_prio.url)

        
    @staticmethod
    def to_json(tarea: Tarea) -> dict:
        return {
            "idd": str(tarea.idd),
            "accionid": str(tarea.accionid),
            "parametros": tarea.parametros,
            "nombre": tarea.nombre,
            "prioridad": tarea.prioridad
        }

    @staticmethod
    def serialize(tarea: Tarea) -> str:
        return json.dumps(TareaRepository.to_json(tarea))


    @staticmethod
    def deserialize(tarea: dict) ->Tarea:
        return Tarea(**tarea)


    def _next_tarea_alta(self):
        return self.tareas_prio.receive_messages(
            MaxNumberOfMessages=MAX_NUMBER_OF_MESSAGES,
            WaitTimeSeconds=POLL_TIME,
            AttributeNames=['MessageDeduplicationId', 'MessageGroupId']
        )
        


    def _next_tarea_baja(self):
        return self.tareas_norm.receive_messages(
                MaxNumberOfMessages=MAX_NUMBER_OF_MESSAGES,
                WaitTimeSeconds=POLL_TIME,
                AttributeNames=['MessageDeduplicationId', 'MessageGroupId']
            )
        

    def next_tarea(self):
        while True:
            self.logger.debug("Esperamos por nueva tarea")
            msg_alta = self._next_tarea_alta()
            if msg_alta.count:
                #self.logger.debug("hay tareas alta 1")
                for cc_alta in msg_alta:
                    cc_alta.delete()
                    #self.logger.debug("Devolvemos tarea alta 1")
                    yield TareaRepository.deserialize(json.loads(cc_alta.body))
            
            msg_baja = self._next_tarea_baja()
            if msg_baja.count:
                #self.logger.debug("Hay tareas baja")
                for cc_baja in msg_baja:
                    msg_alta = self._next_tarea_alta()
                    if msg_alta.count:
                        #self.logger.debug("Hay rtarea alta 2")
                        for cc_alta in msg_alta:
                            cc_alta.delete()
                            #self.logger.debug("Devolvemos tarea alta 2")
                            yield TareaRepository.deserialize(json.loads(cc_alta.body))
                    cc_baja.delete()
                    #self.logger.debug("Devolvemos tarea baja")
                    yield TareaRepository.deserialize(json.loads(cc_baja.body))
            
                

    def append(self, tarea: Tarea):
        cola = self.tareas_prio if tarea.prioridad == Prioridad.ALTA else self.tareas_norm

        cola.send_message(
            MessageBody=TareaRepository.serialize(tarea),
            MessageGroupId=MESSAGE_GROUP_ID,
            MessageDeduplicationId=str(tarea.idd))
        self.logger.debug("Tarea enviada")
