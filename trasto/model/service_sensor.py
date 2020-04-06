from trasto.model.entities import EstadoHumorRepositoryInterface
from trasto.model.value_entities import ResultadoAccion
from trasto.model.events import EventRepositoryInterface


class SensorInterface:

    def listen_to_task_result(self, evento_repo: EventRepositoryInterface) -> None:
        pass


    def update_humor_from_task_result(self, resultado: ResultadoAccion, humor_repo: EstadoHumorRepositoryInterface) -> None:
        pass