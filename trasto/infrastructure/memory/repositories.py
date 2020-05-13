import json
import logging
import uuid

from trasto.model.commands import ComandoNuevaTarea, ComandoRepositoryInterface
from trasto.model.entities import (Accion, AccionRepositoryInterface,
                                   EstadoHumorRepositoryInterface, Idd, Tarea)
from trasto.model.commands import ComandoRepositoryInterface
from trasto.model.value_entities import CambioHumor, IdefierInterface, Prioridad

HUMOR_INICIAL = 0

LIMITE_HUMOR_EUFORICO = 10
LIMITE_HUMOR_ENFADADO = -10


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
        self.humor = HUMOR_INICIAL

    def mejora(self):
        self.humor = self.humor + CambioHumor.HUMOR_MEJORA

    def empeora(self):
        self.humor = self.humor + CambioHumor.HUMOR_EMPEORA

    def que_tal(self):
        return self.humor

    def estas_enfadado(self):
        return self.humor <= LIMITE_HUMOR_ENFADADO

    def estas_euforico(self):
        return self.humor >= LIMITE_HUMOR_EUFORICO

        
