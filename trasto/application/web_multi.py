from traceback import print_exc

from flask import Flask, request, jsonify


from trasto.infrastructure.awsmultiprocess.accion_repository import \
    AccionRepository
from trasto.infrastructure.awsmultiprocess.comando_repository import \
    ComandoRepository
from trasto.infrastructure.memory.repositories import (EstadoDeHumorRepository,
                                                       Idefier,
                                                       LoggerRepository)
from trasto.model.commands import ComandoNuevaAccion, ComandoNuevaTarea
from trasto.model.entities import Accion, Tarea, TipoAccion
from trasto.model.value_entities import Idd

logger = LoggerRepository('web')

accion_repo = AccionRepository()
accion_repo.purge_table()

app = Flask(__name__)

@app.route('/', methods=['GET', ])
def get_service():
    logger.debug("Solicitada get_service")
    return {
        "service": "trastobrain", 
    }



@app.route('/task', methods=['POST'])
def create_task():
    logger.debug("Solicitada new_task")
    comando_repo = ComandoRepository()
    r = request.get_json(force=True)

    comando_repo.send_comando(
        ComandoNuevaTarea(
            idd=Idd(Idefier()),
            tarea=Tarea(
                Idd(Idefier()),
                nombre=r['nombre'],
                accionid=r['accionid'],
                prioridad=r['prioridad']
            )
        )
    )
    logger.debug("Se ha enviado el comando new_task")
    return {
        "msg": "solicitud recibida",
        "request": r}

@app.route('/accion', methods=['POST'])
def new_accion():
    try:
        logger.debug("Solicitada new_accion")
        comando_repo = ComandoRepository()
        r = request.get_json(force=True)
        
        comando_repo.send_comando(
            ComandoNuevaAccion(
                idd=Idd(Idefier()),
                accion=Accion(
                    idd=Idd(Idefier()),
                    nombre=r['nombre'],
                    script_url=r['script_url'],
                    tipo=TipoAccion(r['tipo'])
                )
            )
        )
        return {}
    except KeyError as ke:
        return ({"message": str(ke)}, 400)
    except Exception as ex:
        logger.error(ex)
        print_exc()
        return ({"message": str(ex)}, 500)

        


@app.route('/acciones', methods=['GET'])
def get_all_acciones():
    logger.debug("Solicitada get_all_acciones")
    acciones = accion_repo.get_all_json()
    return {
        "acciones": acciones
    }
