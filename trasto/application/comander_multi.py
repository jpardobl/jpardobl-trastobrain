
from trasto.application.services import Comander
from trasto.infrastructure.awsmultiprocess.accion_repository import \
    AccionRepository
from trasto.infrastructure.awsmultiprocess.comando_repository import \
    ComandoRepository
from trasto.infrastructure.awsmultiprocess.evento_repository import \
    EventoRepository
from trasto.infrastructure.awsmultiprocess.tarea_repository import \
    TareaRepository


def start():
    Comander().listen_to_command(
         ComandoRepository(),
         TareaRepository(),
         AccionRepository(),
         EventoRepository())

if __name__ == '__main__':
    start()    
