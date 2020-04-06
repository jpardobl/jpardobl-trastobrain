
from trasto.model.commands import Comando, ComandoRepositoryInterface
from trasto.model.entities import TareaRepositoryInterface, AccionRepositoryInterface
from trasto.model.events import EventRepositoryInterface
from trasto.model.value_entities import ResultadoAccion


class ComanderInterface:

    def listen_to_command(self, repo_signal: ComandoRepositoryInterface) -> Comando:
        pass

    def enqueue_task(self, comando_repo: ComandoRepositoryInterface, repo_tarea: TareaRepositoryInterface, accion_repo: AccionRepositoryInterface, evento_repo: EventRepositoryInterface) -> None:
        pass
