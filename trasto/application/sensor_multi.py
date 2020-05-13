
from trasto.application.services import Sensor
from trasto.infrastructure.memory.repositories import EstadoDeHumorRepository

from trasto.infrastructure.awsmultiprocess.evento_repository import \
    EventoRepository



def start():
    
    Sensor(EstadoDeHumorRepository()).listen_to_task_result(EventoRepository())


if __name__ == '__main__':
    start()    
