#import uuid, json

from trasto.model.value_entities import (TipoAccion, 
    Prioridad, Idd, CodigoResultado, CambioHumor, ResultadoAccion)


#OBJECTS

class Accion:
    def __init__(self, idd: Idd, nombre: str, script_url: str, tipo: TipoAccion):
        self.idd = idd
        self.nombre = nombre
        self.script_url = script_url
        self.tipo = tipo if isinstance(tipo, TipoAccion) else TipoAccion(nombre=tipo)

    def __str__(self):
        return f"Accion[nombre={self.nombre};tipo={self.tipo}]"

class Tarea:
    #TODO: Hacer que Tarea no use Accion, solo use su idd
    def __init__(self, idd: Idd, nombre: str, accionid: Idd, prioridad: Prioridad, **parametros: dict):
        self.idd = idd
        self.nombre = nombre
        self.accionid = accionid
        self.parametros = parametros
        self.prioridad = prioridad

    def __str__(self):
        return f"Tarea[{self.nombre}], accion: {self.accionid}"

    #def __cmp__(self, other):
    #    return cmp(self.prioridad, other.prioridad)


class EstadoHumorRepositoryInterface:
    def mejora(self) -> None:
        pass

    def empeora(self) -> None:
        pass

    def que_tal(self) -> int:
        pass

    def estas_enfadado(self) -> bool:
        pass

    def estas_euforico(self) -> bool:
        pass

class AccionRepositoryInterface:
    def append(self, accion: Accion) -> None:
        pass
    
    def emit_event_creada_accion(self, accion: Accion) -> bool:
        pass

    def get_all(self) -> tuple:
        pass

    def get_acciones_by_type(self, tipo: TipoAccion) -> tuple:
        pass

    def get_acciones_buen_humor(self) -> tuple:
        pass

    def get_acciones_mal_humor(self) -> tuple:
        pass

    def get_accion_by_id(self, idd: Idd) -> Accion:
        pass
    
    def del_accion(self, accion: Accion) -> bool:
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

