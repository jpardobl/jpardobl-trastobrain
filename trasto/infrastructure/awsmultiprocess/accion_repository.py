
import json

from trasto.infrastructure import AccionNotFoundError
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError
from trasto.infrastructure.awsmultiprocess.aws import \
    get_dynamodb_acciones_table
from trasto.infrastructure.memory.repositories import (Idd, Idefier,
                                                       LoggerRepository)
from trasto.model.entities import Accion, AccionRepositoryInterface
from trasto.model.events import EventRepositoryInterface, NuevaAccionCreada
from trasto.model.value_entities import Idd, TipoAccion



class AccionRepository(AccionRepositoryInterface):
    def __init__(self):
        self.logger = LoggerRepository('accion_repo')
        self.acciones = get_dynamodb_acciones_table()

    def purge_table(self):
        try:
            self.logger.debug(f"Eliminamos todos los elementos de la tabla")
            response = self.acciones.scan()
        except ClientError as ex:
            self.logger.error(f"Error in get_by_type: {ex}")
            return None
        else:
            for each in response['Items']:
                self.acciones.delete_item(Key={'idd': each['idd']})
        
    
    @staticmethod
    def to_json(accion: Accion) -> dict:
        print(accion)
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
        return Accion(**accion)

    def get_acciones_by_type(self, tipo: TipoAccion):
        try:
            self.logger.debug(f"Buscamos accion con el tipo: {tipo}")
            response = self.acciones.scan(
                FilterExpression=Key('tipo').eq(str(tipo)))
        except ClientError as ex:
            self.logger.error(f"Error in get_by_type: {ex}")
            return None
        else:
            for i in response['Items']:
                yield AccionRepository.deserialize(i)

    def get_all(self):
        return tuple(AccionRepository.deserialize(a) for a in self.acciones.scan()['Items'])


    def get_accion_by_id(self, idd: Idd):
        
        try:
            self.logger.debug(f"Buscamos accion con la idd: {idd}")
            response = self.acciones.get_item(Key={'idd': str(idd)})
        except ClientError as ex:
            self.logger.error(f"Error in get_by_id: {ex}")
            return None
        else:
            if not 'Item' in response:
                raise AccionNotFoundError(idd)

            return AccionRepository.deserialize(response['Item'])

    def get_acciones_buen_humor(self):
        return (a for a in self.get_acciones_by_type(TipoAccion(TipoAccion.BUEN_HUMOR)))
    
    def get_acciones_mal_humor(self):
        return (a for a in self.get_acciones_by_type(TipoAccion(TipoAccion.MAL_HUMOR)))

    def del_accion(self, accion: Accion):

        self.acciones.delete_item(
            Key={
                "idd":str(accion.idd)
            }
        )
            
    def rollback_append_accion(self, accion: Accion):
        self.logger.debug("Rolling back append accion")

        self.del_accion(accion)

    def append_accion(self, accion: Accion, evento_repo: EventRepositoryInterface):
        try:
            self.logger.debug(f"Apending nueva accion: tabla: {self.acciones} item: {AccionRepository.to_json(accion)}")
            self.acciones.put_item(Item=AccionRepository.to_json(accion))
            emitido = evento_repo.pub_event(
                NuevaAccionCreada(
                    idd=Idd(idefier=Idefier()),
                    accion_idd=accion.idd,
                    accion_nombre=accion.nombre
                )
            )
            if not emitido:
                self.rollback_append_accion(accion=accion)
        except Exception as ex:
            self.logger.error(ex)
            self.rollback_append_accion(accion=accion)


    def get_all_json(self):
        return tuple(AccionRepository.to_json(accion) for accion in self.get_all())
