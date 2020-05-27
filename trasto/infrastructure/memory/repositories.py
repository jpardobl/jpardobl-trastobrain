import json
import logging
import uuid

from trasto.model.commands import ComandoNuevaTarea, ComandoRepositoryInterface
from trasto.model.entities import (Accion, AccionRepositoryInterface,
                                   EstadoHumorRepositoryInterface, Idd, Tarea, EstadoHumor)
from trasto.model.commands import ComandoRepositoryInterface
from trasto.model.value_entities import IdefierInterface, Prioridad


DEFAULT_LOG_LEVEL = logging.DEBUG


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
            " %(asctime)s %(levelname)7s %(threadName)10s %(lname)22s: %(message)s")

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
        return uuid.uuid4().hex


class EstadoDeHumorRepository(EstadoHumorRepositoryInterface):
    def __init__(self):
        self._humor = EstadoHumor(idd=Idefier())

    def mejora(self):
        self._humor.mejora()

    def empeora(self):
        self._humor.empeora()

    def como_estas(self):
        return self._humor.como_estas()


        
