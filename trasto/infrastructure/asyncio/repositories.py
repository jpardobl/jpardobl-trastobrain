import json
from queue import Empty, Full, PriorityQueue, Queue

from trasto.infrastructure.asyncio import QueueMorph
from trasto.infrastructure.memory.repositories import LoggerRepository,Idefier
from trasto.model.commands import ComandoRepositoryInterface
from trasto.model.entities import (Accion, AccionRepositoryInterface,
                                   Prioridad, Tarea, TareaRepositoryInterface)
from trasto.model.events import EventRepositoryInterface
from trasto.model.value_entities import Idd, ResultadoAccion, TipoAccion

QUEUE_TIMEOUT = 10

tareas = PriorityQueue(maxsize=10)
comandos = QueueMorph()
tareas_para_ejecutar = Queue()
resultados_accion = Queue()
eventos = Queue()

class AccionNotFoundException(Exception):
    pass




class EventoRepository(EventRepositoryInterface):
    def __init__(self):
        self.logger = LoggerRepository('comando_repo')

    def pub_event(self, evento):
        try:
            eventos.put(evento)
            return True
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
        self.acciones = list()

    def get_actiones_by_type(self, tipo: TipoAccion):
        for accion in self.acciones:
            if accion.tipo == tipo:
                yield accion

    def get_all(self):
        return tuple(a for a in self.acciones)


    def get_acciones_by_id(self, idd: Idd):
        self.logger.debug(f"Buscamos accion con la idd: {idd}")
        for accion in self.acciones:
            self.logger.debug(f"Miramos si esta accion {accion} corresponde con id: {idd}")
            if accion.idd == idd:
                return accion
        raise AccionNotFoundException(f"idd={idd}")

    def get_acciones_buen_humor(self):
        return (a for a in self.get_acciones_by_type(TipoAccion(TipoAccion.BUEN_HUMOR)))
    
    def get_acciones_mal_humor(self):
        return (a for a in self.get_acciones_by_type(TipoAccion(TipoAccion.MAL_HUMOR)))

    def del_accion(self, accion: Accion):
        self.acciones.remove(accion)
            
    def rollback_append_accion(self, accion: Accion):
        self.logger.debug("Rolling back append accion")
        self.del_accion(accion)

    def append_accion(self, accion: Accion, evento_repo: EventRepositoryInterface):
        try:
            self.logger.debug("Apending nueva accion")
            self.acciones.append(accion)
            emitido = evento_repo.pub_event(accion)
            if not emitido:
                self.rollback_append_accion(accion=accion)
        except Exception as ex:
            self.logger.error(ex)
            self.rollback_append_accion(accion=accion)

    def to_json(self, accion: Accion):
        return json.dumps({
            "idd": f"{accion.idd}",
            "nombre": accion.nombre,
            "script_url": accion.script_url,
            "tipo": f"{accion.tipo}"
        })

    def from_json(self, json_str_accion: str):
        json_accion = json.loads(json_str_accion)
        return Accion(
            idd=Idd(idefier=Idefier(), idd_str=json_accion['idd']),
            nombre=json_accion['nombre'],
            script_url=json_accion['script_url'],
            tipo=json_accion['tipo']
        )

    def get_all_json(self):
        return tuple(json.loads(self.to_json(accion)) for accion in self.get_all())
