import asyncio
import json
import random
import time
import traceback

from trasto.infrastructure.asyncio.repositories import AccionNotFoundException
from trasto.infrastructure.memory.repositories import Idefier, LoggerRepository
from trasto.model.commands import (ComandoNuevaAccion, ComandoNuevaTarea,
                                   ComandoRepositoryInterface, ComandoNuevaTareaLibreAlbedrio)
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
                    self.logger.debug(f"Se ha terminado la accion: {evento.tarea_idd}, resultado: {evento.resultado}")
                    self.update_humor_from_task_result(evento.resultado, self.humor_repo, evento_repo)
                    self.logger.debug("Escuchando a resultado de tarea")
        except Exception as ex:
            self.logger.error(ex)
            traceback.print_exc()


    def update_humor_from_task_result(self, resultado: ResultadoAccion, humor_repo: EstadoHumorRepositoryInterface, evento_repo: EventRepositoryInterface):
        try:
            print(resultado)
            humor_repo.mejora() if resultado.is_good() else humor_repo.empeora()
            self.logger.debug("el humor ha cambiado a : {}".format(humor_repo.que_tal()))
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
            idd = Idd(idefier=id_repo, idd_str=accionid)
            self.logger.debug(f"Intentamos ejecutar accionid: {idd}, repo: {accion_repo}")
            accion = accion_repo.get_acciones_by_id(idd)
            self.logger.debug(f"Ejecutamos: {accion} (dormimos 10s)")

            #TODO implementar realmente la ejecucion, ahora solo hay un ejemplo
            time.sleep(10)
            self.logger.debug("despertamos, tarea ejecutada")
            resultado = None
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
        except AccionNotFoundException as ex:
            resultado = ResultadoAccion(
                codigo=CodigoResultado(codigo=CodigoResultado.MAL_RESULTADO),
                msg="No existe la tarea"
            )
            evento = AccionTerminada(
                idd=Idd(idefier=Idefier()), 
                tarea_idd=tarea.idd,
                resultado=resultado)
        finally:
            evento_repo.pub_event(evento=evento)
        

class Comander(ComanderInterface):
    def __init__(self):
        self.logger = LoggerRepository('comander')

    def enqueue_task(self, tarea: Tarea, tarea_repo: TareaRepositoryInterface):
        self.logger.debug(f"encolando tarea {tarea}")
        tarea_repo.append(tarea)

    def listen_to_command(self, repo_command: ComandoRepositoryInterface, tarea_repo: TareaRepositoryInterface, accion_repo: AccionRepositoryInterface, evento_repo: EventRepositoryInterface):
        self.logger.debug("Escuchando por nuevo comando")
        while True:
            try:
                cmd = repo_command.next_comando()
                if isinstance(cmd, ComandoNuevaTarea):
                    self.enqueue_task(cmd.tarea, tarea_repo)
                    continue
                if isinstance(cmd, ComandoNuevaAccion):
                    self.logger.debug("El comando es crear una accion")
                    accion_repo.append_accion(accion=cmd.accion, evento_repo=evento_repo)

                    continue
                raise CommandNotImplemented(cmd)

            except Exception as ex:
                self.logger.error(ex)
                traceback.print_exc()
        

async def librealbedrio(comando_repo, humor_repo):
    logger = LoggerRepository('librealbedrio')
    while True:
        rnd = random.randrange(10, 60)
        logger.debug("Esperamos {rnd} para actuar")
        await asyncio.sleep(rnd)
        cmd = ComandoNuevaTareaLibreAlbedrio(idd=Idd(Idefier()))
        humor = humor_repo.que_tal()
        logger.debug(f"Hemos despertado, vemos que estamos con el humor: {humor}")
        acciones = ()
        if not humor_repo.estas_enfadado() and not humor_repo.estas_euforico():
            logger.debug("No hacemos nada porque ni estamos euforicos, ni enfadados")
            continue
        cmd = ComandoNuevaTareaLibreAlbedrio(idd=Idd(Idefier))
        await comando_repo.send_comando(cmd)
        logger.debub("Acabamos de enviar un comando de libre albedrio")



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
        logger.error(mgr_ex)
