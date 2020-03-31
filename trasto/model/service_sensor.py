from trasto.model.entities import ResultadoAccionRepositoryInterface, EstadoHumorRepositoryInterface
from trasto.model.value_entities import ResultadoAccion


class SensorInterface:

    def listen_to_task_result(self, repo_resultado: ResultadoAccionRepositoryInterface) -> None:
        pass


    def update_humor_from_task_result(self, resultado: ResultadoAccion, humor_repo: EstadoHumorRepositoryInterface) -> None:
        pass