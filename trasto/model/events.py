

from trasto.model.entities import Accion
from trasto.model.value_entities import Idd, IdefierInterface, ResultadoAccion


class Evento:
    def __init__(self, idd:IdefierInterface):
        self._idd = idd
    
    @property
    def idd(self):
        return self._idd

class NuevaAccionCreada(Evento):
    def __init__(self, idd: IdefierInterface, accion_idd: IdefierInterface, accion_nombre: str):
        super().__init__(idd)
        self._accion_idd = accion_idd
        self._accion_nombre = accion_nombre


class AccionTerminada(Evento):
    def __init__(self, idd: IdefierInterface, tarea_idd: IdefierInterface, resultado: ResultadoAccion):
        super().__init__(idd)
        self._tarea_idd = tarea_idd
        self._resultado = resultado

    @property
    def tarea_idd(self):
        return self._tarea_idd

    @property
    def resultado(self):
        return self._resultado

class EstadoHumorCambiado(Evento):
    def __init__(self, idd: IdefierInterface, nuevo_estado_humor: int):
        super().__init__(idd)
        self.nuevo_estado_humor = nuevo_estado_humor


class EventRepositoryInterface:
    def pub_event(self, evento: Evento) -> bool:
        pass

    def subscribe_event(self) -> Evento:
        pass
