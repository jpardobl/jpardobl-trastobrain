import json
import logging
import uuid

from trasto.model.commands import ComandoNuevaTarea, ComandoRepositoryInterface
from trasto.model.entities import (Accion, AccionRepositoryInterface,
                                   EstadoHumorRepositoryInterface, Idd,
                                   TipoAccion, Tarea, Accion)
from trasto.model.commands import ComandoRepositoryInterface
from trasto.model.value_entities import CambioHumor, IdefierInterface, Prioridad

HUMOR_INICIAL = 0

DEFAULT_LOG_LEVEL = logging.DEBUG

acciones = list()


class LoggerRepository:

    def __init__(self, lname, level=None):
        logger = logging.getLogger(lname)
        final_level = DEFAULT_LOG_LEVEL if level is None else level
        logger.setLevel(final_level)
        handler = logging.StreamHandler()

        for h in logger.handlers:
            logger.removeHandler(h)

        logger.addHandler(handler)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)7s %(threadName)10s %(lname)22s %(filename)12s:%(lineno)s: %(message)s")

        handler.setFormatter(formatter)
    
        logger = logging.LoggerAdapter(logger, {'lname': lname})    
        #if final_level == logging.DEBUG:
        #    logger = logging.LoggerAdapter(logger, {'lname': f"{lname}-{shortuuid.uuid()}"})
        #else:
            
        self.logger = logger

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)

    def crit(self, msg):
        self.logger.critical(msg)


class Idefier(IdefierInterface):
    def create_new_id(self):
        return uuid.uuid1()


class EstadoDeHumorRepository(EstadoHumorRepositoryInterface):
    def __init__(self):
        self.humor = HUMOR_INICIAL

    def mejora(self):
        self.humor = self.humor + CambioHumor.HUMOR_MEJORA

    def empeora(self):
        self.humor = self.humor + CambioHumor.HUMOR_EMPEORA

    def que_tal(self):
        return f"{self.humor}"


class AccionRepository(AccionRepositoryInterface):

    def get_action_by_type(self, tipo: TipoAccion):
        for accion in acciones:
            if accion.tipo == tipo:
                yield accion


    def append_accion(self, accion: Accion):
        acciones.append(accion)


class ComandoRepository(ComandoRepositoryInterface):

    def __init__(self):
        self.logger = LoggerRepository("ComandoRepository")

    def next_commando(self):
        nombre = input('Introduce un numero:')
        #nombre = "5"
        yield ComandoNuevaTarea(
            idd=Idd(Idefier()),
            tarea=Tarea(
                idd=Idd(Idefier()),
                nombre=nombre,
                accion=Accion(Idd(Idefier()), "accion", "script", TipoAccion("normal")),
                prioridad=Prioridad(1)
            ))
