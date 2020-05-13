from trasto.application.services import Ejecutor
from trasto.infrastructure.awsmultiprocess.accion_repository import \
    AccionRepository
from trasto.infrastructure.awsmultiprocess.comando_repository import \
    ComandoRepository
from trasto.infrastructure.awsmultiprocess.evento_repository import \
    EventoRepository
from trasto.infrastructure.awsmultiprocess.tarea_repository import \
    TareaRepository

from trasto.infrastructure.memory.repositories import Idefier


def start():
    Ejecutor().listen_for_next_tarea(Idefier(), TareaRepository(), EventoRepository(), AccionRepository())

if __name__ == '__main__':
    start()    
