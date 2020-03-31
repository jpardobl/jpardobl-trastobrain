import asyncio
import json
import traceback

from trasto.infrastructure.asyncio.repositories import (
    ResultadoAccionRepository, TareaRepository)
from trasto.infrastructure.memory.repositories import (EstadoDeHumorRepository,
                                                       LoggerRepository,
                                                       ComandoRepository)
from trasto.model.entities import (Accion, CodigoResultado,
                                   ResultadoAccion, Tarea)
from trasto.model.commands import ComandoNuevaTarea

from trasto.model.service_comander import ComanderInterface
from trasto.model.service_ejecutor import EjecutorInterface
from trasto.model.service_sensor import SensorInterface
from trasto.model.value_entities import Prioridad, TipoAccion


class CommandNotImplemented(Exception):
    pass


class Sensor(SensorInterface):
    def __init__(self, humor_repo: EstadoDeHumorRepository):
        self.logger = LoggerRepository('sensor')
        self.humor_repo = humor_repo

    def listen_to_task_result(self, repo_resultado: ResultadoAccionRepository):
        try:
            self.logger.debug("Escuchando a resultado de tarea")
            for tarea in repo_resultado.next_resultado():
                self.logger.debug(f"Ha llegado resultado de una tarea: {tarea.resultado}")
                self.update_humor_from_task_result(tarea.resultado, self.humor_repo)
                self.logger.debug("Escuchando a resultado de tarea")
        except Exception as ex:
            self.logger.error(ex)
            traceback.print_exc()


    def update_humor_from_task_result(self, resultado: ResultadoAccion, humor_repo: EstadoDeHumorRepository):
        try:
            humor_repo.mejora() if resultado.is_good() else humor_repo.empeora()
            self.logger.debug("el humor ha cambiado a : {}".format(humor_repo.que_tal()))
        except Exception as ex:
            self.logger.error(ex)
            traceback.print_exc()


class Ejecutor(EjecutorInterface):
    def __init__(self):
        self.logger = LoggerRepository('ejecutor')

    def listen_for_next_tarea(self, tarea_repo: TareaRepository, resultado_repo: ResultadoAccionRepository):
        try:
            self.logger.debug("Escuchando por nueva tarea")
            for tarea in tarea_repo.next_tarea():
                self.ejecuta_tarea(tarea, resultado_repo)
                self.logger.debug("Escuchando por nueva tarea")
        except Exception as ex:
            self.logger.error(ex)
            traceback.print_exc()


    def ejecuta_tarea(self, tarea: Tarea, resultado_repo: ResultadoAccionRepository): 
        accion = tarea.accion
        self.logger.debug(f"Ejecutamos: {accion.nombre}")
        resultado_repo.send_resultado(
            tarea=tarea,
            resultado=ResultadoAccion( 
                codigo=CodigoResultado(CodigoResultado.BUEN_RESULTADO if int(tarea.nombre)> 0 else CodigoResultado.MAL_RESULTADO), 
                msg="buena!!!"))


class Comander(ComanderInterface):
    def __init__(self):
        self.logger = LoggerRepository('comander')

    def enqueue_task(self, tarea: Tarea, tarea_repo: TareaRepository):
        self.logger.debug(f"encolando tarea {tarea}")
        tarea_repo.append(tarea)

    def listen_to_command(self, repo_command: ComandoRepository, tarea_repo: TareaRepository):

        try:
            for cmd in repo_command.next_comando():
                print(cmd)
                if isinstance(cmd, ComandoNuevaTarea):
                    self.enqueue_task(cmd, tarea_repo)
                    continue
                raise CommandNotImplemented(cmd)

        except Exception as ex:
            self.logger.error(ex)
            traceback.print_exc()
        

async def brain(thread_executor, resultado_repo, tarea_repo, comando_repo, humor_repo):
    logger = LoggerRepository('brain')
    try:

        loop = asyncio.get_event_loop()
        blocking_tasks = [
            loop.run_in_executor(thread_executor, Sensor(humor_repo).listen_to_task_result, resultado_repo),
            loop.run_in_executor(thread_executor, Ejecutor().listen_for_next_tarea, tarea_repo, resultado_repo),
            loop.run_in_executor(thread_executor, Comander().listen_to_command, comando_repo, tarea_repo)
        ]
        logger.debug("Preparados los threads")
        return blocking_tasks
    except asyncio.CancelledError:
        pass

    except Exception as mgr_ex:
        logger.error(mgr_ex)
