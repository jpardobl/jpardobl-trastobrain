
from queue import Empty, Full, PriorityQueue, Queue

from trasto.infrastructure.asyncio import QueueMorph

from trasto.infrastructure.memory.repositories import LoggerRepository
from trasto.model.entities import (Prioridad,
                                   ResultadoAccionRepositoryInterface, Tarea, Accion, 
                                   TareaRepositoryInterface, AccionRepositoryInterface)

from trasto.model.events import EventRepositoryInterface
from trasto.model.value_entities import ResultadoAccion, Idd, TipoAccion                           
from trasto.model.commands import ComandoRepositoryInterface


QUEUE_TIMEOUT = 10

tareas = PriorityQueue(maxsize=10)
comandos = QueueMorph()
tareas_para_ejecutar = Queue()
resultados_accion = Queue()
eventos = Queue()
acciones = list()


class AccionNotFoundException(Exception):
    pass


class EventoRepository(EventRepositoryInterface):
    def __init__(self):
        self.logger = LoggerRepository('comando_repo')

    def pub_event(self, evento):
        try:
            eventos.put(evento)
        except Exception:
            return False

    def subscribe_event(self):
        while True:
            try:
                yield eventos.get(block=True, timeout=QUEUE_TIMEOUT)
            except Exception as ex:
                self.logger.error(ex)
                continue
                

class TareaRepository(TareaRepositoryInterface):

    def __init__(self):
        self.logger = LoggerRepository('tarea_repo')

    def next_tarea(self):
        while True:
            try:
                self.logger.debug("esperando por tarea")
                yield tareas.get(block=True, timeout=QUEUE_TIMEOUT)
            except Empty:
                pass


    def append(self, tarea: Tarea):
        try:
            tareas.put(tarea)
        except:
            self.logger.crit("Cola de tareas llena!!!!")
    


class ResultadoAccionRepository(ResultadoAccionRepositoryInterface):
    def __init__(self):
        self.logger = LoggerRepository('resultados_accion_repo')

    def next_resultado(self):
        while True:
            try:
                yield resultados_accion.get(block=True, timeout=QUEUE_TIMEOUT)
            except Empty:
                pass
        

    def send_resultado(self, tarea: Tarea, resultado: ResultadoAccion):
        try:
            tarea.set_resultado(resultado)
            resultados_accion.put(tarea)
        except Full:
            self.logger.crit("Cola resultado accion llena!!!!")


class ComandoRepository(ComandoRepositoryInterface):
    def __init__(self):
        self.logger = LoggerRepository('comando_repo')

    def next_comando(self):
        while True:
            try:
                self.logger.debug("Esperamos por nuevo comando")
                return comandos.get()
            except Empty:
                pass

    async def send_comando(self, comando):
        await comandos.aput(comando)
        self.logger.debug("Comando enviado")


class AccionRepository(AccionRepositoryInterface):
    def __init__(self):
        self.logger = LoggerRepository('accion_repo')

    def get_action_by_type(self, tipo: TipoAccion):
        for accion in acciones:
            if accion.tipo == tipo:
                yield accion


    def get_accion_by_id(self, idd):
        for accion in acciones:
            if accion.idd == idd:
                return accion
        raise AccionNotFoundException(f"idd={idd}")

    def del_accion(self, accion: Accion):
        acciones.remove(accion)
            
    def rollback_append_accion(self, accion: Accion):
        self.del_accion(accion)

    def append_accion(self, accion: Accion, evento_repo: EventRepositoryInterface):
        try:
            acciones.append(accion)
            emitido = evento_repo.pub_event(accion)
            if not emitido:
                self.rollback_append_accion(accion=accion)
        except Exception as ex:
            self.logger.error(ex)
            self.rollback_append_accion(accion=accion)
            


