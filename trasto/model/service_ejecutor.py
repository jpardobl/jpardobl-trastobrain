from trasto.model.entities import TareaRepositoryInterface, EstadoHumorRepositoryInterface
from trasto.model.entities import Tarea
from trasto.model.events import EventRepositoryInterface


class EjecutorInterface:

    def __init__(self, humor: EstadoHumorRepositoryInterface) -> None:
        pass

    def listen_for_next_tarea(self, tarea_repo: TareaRepositoryInterface) -> Tarea:
        pass

    def ejecuta_tarea(self, tarea: Tarea,  evento_repo: EventRepositoryInterface) -> None:
        pass