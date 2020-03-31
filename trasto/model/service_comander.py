
from trasto.model.commands import Comando, ComandoRepositoryInterface
from trasto.model.entities import TareaRepositoryInterface
from trasto.model.value_entities import ResultadoAccion


class ComanderInterface:

    def listen_to_command(self, repo_signal: ComandoRepositoryInterface) -> Comando:
        pass

    def enqueue_task(self, command: ComandoRepositoryInterface, repo_tarea: TareaRepositoryInterface) -> None:
        pass