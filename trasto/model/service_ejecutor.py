from trasto.model.entities import TareaRepositoryInterface, EstadoHumorRepositoryInterface, ResultadoAccionRepositoryInterface
from trasto.model.entities import Tarea

class EjecutorInterface:

    def __init__(self, humor: EstadoHumorRepositoryInterface) -> None:
        pass

    def listen_for_next_tarea(self, tarea_repo: TareaRepositoryInterface) -> Tarea:
        pass

    def ejecuta_tarea(self, tarea: Tarea,  resultado_repo: ResultadoAccionRepositoryInterface) -> None:
        pass