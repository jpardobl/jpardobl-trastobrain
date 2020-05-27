#import uuid, json

from trasto.model.value_entities import (TipoAccion, 
    Prioridad, Idd, CodigoResultado, ResultadoAccion)


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
    
    def __init__(self, idd: Idd, nombre: str, accionid: Idd, prioridad: Prioridad, **parametros: dict):
        self.valida_nombre(nombre)
        self.idd = idd
        self.nombre = nombre
        self.accionid = accionid
        self.parametros = parametros
        self.prioridad = prioridad

    def valida_nombre(self, nombre):

        if len(nombre) < 3:
            raise AttributeError("El nombre no es valido, tiene que tener al menos 3 caracteres")
        if not nombre[0].isupper():
            raise AttributeError("El nombre no es valido, la primera debe ser mayucula")


    def __str__(self):
        return f"Tarea[{self.nombre}], accion: {self.accionid}"

    #def __cmp__(self, other):
    #    return cmp(self.prioridad, other.prioridad)

class EstadoHumor:
    def __init__(self, idd: Idd):
        self._idd = idd
        self._estado = 0

    def mejora(self):
        self._estado = self._estado + 1

    def empeora(self):
        self._estado = self._estado - 1

    def como_estas(self):
        if self.estado == 0:
            return "Normal"
        if self.estado > 2:
            return "Muy bien"
        if self.estado > 0:
            return "Bien"
        if self.estado < -2:
            return "Muy mal"
        if self.estado < 0:
            return "Mal"

    @property
    def estado(self):
        return int(self._estado)

class EstadoHumorRepositoryInterface:
    def guarda(self, estado: EstadoHumor) -> None:
        pass

    def emit_event_estado_humor_cambiado(self,  nuevo_estado: EstadoHumor)-> None:
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

