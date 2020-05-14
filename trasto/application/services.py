import asyncio
import json
import random
import time
import traceback

from trasto.infrastructure import AccionNotFoundError
from trasto.infrastructure.memory.repositories import Idefier, LoggerRepository
from trasto.model.commands import (ComandoNuevaAccion, ComandoNuevaTarea,
                                   ComandoRepositoryInterface)
from trasto.model.entities import (Accion, AccionRepositoryInterface,
                                   CodigoResultado,
                                   EstadoHumorRepositoryInterface,
                                   ResultadoAccion, Tarea,
                                   TareaRepositoryInterface)
from trasto.model.events import (AccionTerminada, Evento,
                                 EventRepositoryInterface, EstadoHumorCambiado)
from trasto.model.service_comander import ComanderInterface
from trasto.model.service_ejecutor import EjecutorInterface
from trasto.model.service_sensor import SensorInterface
from trasto.model.value_entities import (Idd, IdefierInterface, Prioridad,
                                         TipoAccion)



class CommandNotImplemented(Exception):
    pass


class Sensor(SensorInterface):

    def __init__(self, humor_repo: EstadoHumorRepositoryInterface):
        self.logger = LoggerRepository('sensor')
        self.humor_repo = humor_repo


    def listen_to_task_result(self, evento_repo: EventRepositoryInterface):
        try:
            self.logger.debug("Escuchando a resultado de tarea")
            for evento in evento_repo.subscribe_event():
                if isinstance(evento, AccionTerminada):
                    self.logger.debug(f"Se ha terminado la tarea: {evento.tarea_idd}, resultado: {evento.resultado}")
                    self.update_humor_from_task_result(evento.resultado, self.humor_repo, evento_repo)
                self.logger.debug("Escuchando por un resultado de tarea")
        except Exception as ex:
            self.logger.error(ex)
            traceback.print_exc()


    def update_humor_from_task_result(self, resultado: ResultadoAccion, humor_repo: EstadoHumorRepositoryInterface, evento_repo: EventRepositoryInterface):
        try:
            print(resultado)
            humor_repo.mejora() if resultado.is_good() else humor_repo.empeora()
            self.logger.debug("El humor ha cambiado a : {}".format(humor_repo.que_tal()))
            evento_repo.pub_event(EstadoHumorCambiado(
                idd=Idd(Idefier()),
                nuevo_estado_humor=humor_repo.que_tal()))
        except Exception as ex:
            self.logger.error(ex)
            traceback.print_exc()


class Ejecutor(EjecutorInterface):
    def __init__(self):
        self.logger = LoggerRepository('ejecutor')

    def listen_for_next_tarea(self, id_repo: IdefierInterface, tarea_repo: TareaRepositoryInterface, evento_repo: EventRepositoryInterface, accion_repo: AccionRepositoryInterface):
        try:
            self.logger.debug("Escuchando por nueva tarea")
            for tarea in tarea_repo.next_tarea():

                self.ejecuta_tarea(tarea=tarea, id_repo=id_repo, evento_repo=evento_repo, accion_repo=accion_repo)
                self.logger.debug("Escuchando por nueva tarea")
        except Exception as ex:
            self.logger.error(ex)
            traceback.print_exc()


    def ejecuta_tarea(self, tarea: Tarea, id_repo:IdefierInterface, evento_repo: EventRepositoryInterface, accion_repo: AccionRepositoryInterface): 
        
        evento = None
        resultado = None
        try:
            accionid = tarea.accionid
            print(f"ha llegado el accion id: {accionid}")
            idd = Idd(idefier=id_repo, idd_str=accionid)
            self.logger.debug(f"Intentamos ejecutar ---- accionid: {idd}, repo: {accion_repo}")
            accion = accion_repo.get_accion_by_id(idd)
            self.logger.debug(f"Ejecutamos: {accion} (dormimos 10s)")

            #TODO implementar realmente la ejecucion, ahora solo hay un ejemplo
            time.sleep(10)
            self.logger.debug("despertamos, tarea ejecutada")
            
            if int(tarea.nombre) > 0:
                resultado = ResultadoAccion(
                    codigo=CodigoResultado(codigo=CodigoResultado.BUEN_RESULTADO),
                    msg="la tarea ha ido bien"
                )
            else:
                resultado = ResultadoAccion(
                    codigo=CodigoResultado(codigo=CodigoResultado.MAL_RESULTADO),
                    msg="la tarea ha ido mal"
                )
            evento = AccionTerminada(
                idd=Idd(idefier=Idefier()), 
                tarea_idd=tarea.idd,
                resultado=resultado)
            evento_repo.pub_event(evento=evento)
            
        except AccionNotFoundError as exx:
            self.logger.error(f"No se ha encontrado la Accion {exx}")
            resultado = ResultadoAccion(
                codigo=CodigoResultado(codigo=CodigoResultado.MAL_RESULTADO),
                msg=f"No existe la tarea {exx}"
            )
            evento = AccionTerminada(
                idd=Idd(idefier=Idefier()), 
                tarea_idd=tarea.idd,
                resultado=resultado)
            evento_repo.pub_event(evento=evento)
        except Exception as ekk:
            self.logger.error(f"Error no identificado: {ekk}")

            
        

class Comander(ComanderInterface):
    def __init__(self):
        self.logger = LoggerRepository('comander')

    def enqueue_task(self, tarea: Tarea, tarea_repo: TareaRepositoryInterface):
        self.logger.debug(f"Encolando tarea {tarea}")
        tarea_repo.append(tarea)

    def listen_to_command(self, repo_command: ComandoRepositoryInterface, tarea_repo: TareaRepositoryInterface, accion_repo: AccionRepositoryInterface, evento_repo: EventRepositoryInterface):
        self.logger.debug("Escuchando por nuevo comando")
        #while True:   
        for cmd in repo_command.next_comando():   
            try:
                #cmd = repo_command.next_comando()
                if isinstance(cmd, ComandoNuevaTarea):
                    self.logger.debug("Recibido comando de tipo ComandoNuevaTarea")
                    self.enqueue_task(cmd.tarea, tarea_repo)
                    self.logger.debug("Escuchando por nuevo comando")
                    continue
                if isinstance(cmd, ComandoNuevaAccion):
                    self.logger.debug("Recibido comando de tipo ComandoNuevaAccion")
                    accion_repo.append_accion(accion=cmd.accion, evento_repo=evento_repo)
                    self.logger.debug("Escuchando por nuevo comando")
                    continue
                raise CommandNotImplemented(cmd)

            except Exception as ex:
                self.logger.error(ex)
                traceback.print_exc()
        


async def brain(thread_executor, id_repo, tarea_repo, comando_repo, humor_repo, accion_repo, evento_repo):
    logger = LoggerRepository('brain')
    try:

        loop = asyncio.get_event_loop()
        blocking_tasks = [
            loop.run_in_executor(thread_executor, Sensor(humor_repo).listen_to_task_result, evento_repo),
            loop.run_in_executor(thread_executor, Ejecutor().listen_for_next_tarea, id_repo, tarea_repo, evento_repo, accion_repo),
            loop.run_in_executor(thread_executor, Comander().listen_to_command, comando_repo, tarea_repo, accion_repo, evento_repo)
        ]
        
        logger.debug("Preparados los threads")
        return blocking_tasks
    except asyncio.CancelledError:
        pass

    except Exception as mgr_ex:
        logger.error(f"Excecion en brain: {mgr_ex}")
