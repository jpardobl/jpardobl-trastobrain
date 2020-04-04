import uuid, json

from trasto.model.value_entities import (TipoAccion, 
    Prioridad, Idd, CodigoResultado, CambioHumor, ResultadoAccion)


#OBJECTS

class Accion:
    def __init__(self, idd: Idd, nombre: str, script_url: str, tipo: TipoAccion):
        self.idd = idd
        self.nombre = nombre
        self.script_url = script_url
        self.tipo = tipo

    def __str__(self):
        return f"Accion[nombre={self.nombre};tipo={self.tipo}]"

class Tarea:
    def __init__(self, idd: Idd, nombre: str, accion: Accion, prioridad: Prioridad, **parametros: dict):
        self.id = idd
        self.nombre = nombre
        self.accion = accion
        self.parametros = parametros
        self.prioridad = prioridad
        self.resultado = None

    def __str__(self):
        return f"Tarea[{self.nombre}], accion: {self.accion}"

    def __cmp__(self, other):
        return cmp(self.prioridad, other.prioridad)

    def set_resultado(self, resultado: ResultadoAccion):
        self.resultado = resultado


class EstadoHumorRepositoryInterface:
    def mejora(self) -> None:
        pass

    def empeora(self) -> None:
        pass

    def que_tal(self):
        pass

        
class ResultadoAccionRepositoryInterface:
    def next_resultado(self) -> Tarea:
        pass

    def send_resultado(self, tarea: Tarea, resultado: ResultadoAccion):
        pass


class AccionRepositoryInterface:
    def append(self, accion: Accion) -> None:
        pass
    
    def emit_event_creada_accion(self, accion: Accion) -> bool:
        pass
    
    def get_accion_by_type(self, tipo: TipoAccion) -> tuple:
        pass

    def get_accion_by_id(self, idd: Idd) -> Accion:
        pass
    

class TareaRepositoryInterface:
    def next_tarea(self) -> Tarea:
        """Retrieves the next Tarea from the queue. It looks before for high priority ones"""
        pass

    def append(self, tarea: Tarea) -> None:
        """Appends a new Tarea taking priority into account"""
        pass

    def ejecuta(self, tarea: Tarea) -> None:
        pass

    def next_tarea_para_ejecutar(self) -> Tarea:
        pass

