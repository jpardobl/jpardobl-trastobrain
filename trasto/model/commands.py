from trasto.model.value_entities import Idd
from abc import ABC

from trasto.model.entities import Tarea



class Comando(ABC):
    pass


class ComandoNuevaTarea(Comando):
    def __init__(self, idd: Idd, tarea: Tarea):
        self.idd = idd
        self.tarea = tarea

    def __str__(self):
        return f"idd: {self.idd}, tarea: {self.tarea}"


class ComandoRepositoryInterface:
    def next_comando(self) -> Comando:
        pass

    def send_comando(self, comando: Comando) -> None:
        pass

