
import json

from trasto.infrastructure.memory.repositories import Idd, LoggerRepository
from trasto.model.entities import Accion, AccionRepositoryInterface
from trasto.model.events import EventRepositoryInterface
from trasto.model.value_entities import Idd, TipoAccion
from trasto.infrastructure.aws_multiprocess.aws import create_dynamodb_acciones_table




class AccionNotFoundException(Exception):
    pass


class AccionRepository(AccionRepositoryInterface):
    def __init__(self):
        self.logger = LoggerRepository('accion_repo')
        self.table = None

    def set_table(self):
        self.table = create_or_get_dynamodb(
            table_name=TABLE_NAME,
            key_schema=KEY_SCHEMA,
            attributes=ATTRIBUTES
        )

    @staticmethod
    def to_json(accion: Accion) -> dict:
        return {
            "idd": str(accion.idd),
            "nombre": accion.nombre,
            "script_url": accion.script_url,
            "tipo": str(accion.tipo)
        }

    @staticmethod
    def serialize(accion: Accion) -> str:
        return json.dumps(AccionRepository.to_json(accion))

    @staticmethod
    def deserialize(accion: dict) -> Accion:
        return Accion(
            idd=accion['idd'],
            nombre=accion['nombre'],
            script_url=accion['script_url'],
            tipo=accion['tipo']
        )

    def get_actiones_by_type(self, tipo: TipoAccion):
        self.set_table()
        for accion in self.acciones:
            if accion.tipo == tipo:
                yield accion

    def get_all(self):
        return tuple(a for a in self.table.query())


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
        self.set_table()
        self.table.delete_item(
            Key={
                "idd":str(accion.idd)
            }
        )
            
    def rollback_append_accion(self, accion: Accion):
        self.logger.debug("Rolling back append accion")
        self.set_table()
        self.del_accion(accion)

    def append_accion(self, accion: Accion, evento_repo: EventRepositoryInterface):
        try:
            self.set_table()

            self.logger.debug(f"Apending nueva accion: tabla: {self.table}item: {AccionRepository.to_json(accion)}")
            self.table.put_item(Item=AccionRepository.to_json(accion))
            emitido = evento_repo.pub_event(accion)
            if not emitido:
                self.rollback_append_accion(accion=accion)
        except Exception as ex:
            self.logger.error(ex)
            self.rollback_append_accion(accion=accion)


    def get_all_json(self):
        return tuple(json.loads(AccionRepository.to_json(accion)) for accion in self.get_all())
