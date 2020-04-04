

from trasto.model.entities import Accion
from trasto.model.value_entities import Idd, IdefierInterface


class Evento:
    pass


class CreadaNuevaAccion(Evento):
    def __init__(self, idd: IdefierInterface, accion_idd: IdefierInterface, accion_nombre: str):
        self.idd = idd
        self.accion_idd = accion_idd
        self.accion_nombre = accion_nombre


class EventRepositoryInterface:
    def pub_event(self, evento: Evento) -> bool:
        pass

    def subscribe_event(self) -> Evento:
        pass
