import asyncio
from concurrent.futures import ThreadPoolExecutor

from aiohttp import web

from trasto.infrastructure.asyncio.repositories import (
    AccionRepository, ComandoRepository, EventoRepository,
    TareaRepository)
from trasto.infrastructure.asyncio.services import brain
from trasto.infrastructure.memory.repositories import (EstadoDeHumorRepository,
                                                       Idefier)
from trasto.model.commands import ComandoNuevaAccion, ComandoNuevaTarea
from trasto.model.entities import Accion, Tarea, TipoAccion
from trasto.model.value_entities import Idd

accion_repo = AccionRepository()

async def get_service(request):

    return web.json_response({
        "service": "trastobrain", 
    })


async def new_task(request):
    comando_repo = ComandoRepository()
    r = await request.json()

    await comando_repo.send_comando(
        ComandoNuevaTarea(
            idd=Idd(Idefier()),
            tarea=Tarea(
                Idd(Idefier()),
                nombre=r['nombre'],
                accion=r['accion'],
                prioridad=r['prioridad']
            )
        )
    )
    return web.json_response({
        "msg": "solicitud recibida",
        "request": r
    })


async def new_accion(request):
    comando_repo = ComandoRepository()
    r = await request.json()
    
    await comando_repo.send_comando(
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


async def get_all_acciones(request):
    acciones = accion_repo.get_all_json()
    type(acciones)
    return web.json_response({
        "acciones": acciones
    })


class ScraperServer:

    def __init__(self, host, port, accion_repo, loop=None):

        self.host = host
        self.port = port

        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.accion_repo = accion_repo

    async def start_background_tasks(self, app):

        t_executor = ThreadPoolExecutor(
            max_workers=10
        )

        humor_repo = EstadoDeHumorRepository()
        tarea_repo = TareaRepository()
        comando_repo = ComandoRepository()

        evento_repo = EventoRepository()

        app['brain'] = self.loop.create_task(brain(
            thread_executor=t_executor,
            tarea_repo=tarea_repo,
            comando_repo=comando_repo,
            humor_repo=humor_repo,
            accion_repo=self.accion_repo,
            evento_repo=evento_repo))

    async def cleanup_background_tasks(self, app):
        app['brain'].cancel()
        await app['brain']


    async def create_app(self):
        app = web.Application()
        app.router.add_get('/', get_service)
        app.router.add_post('/task', new_task)
        app.router.add_post('/accion', new_accion)
        app.router.add_get('/acciones', get_all_acciones)
        return app


    def run_app(self):
        loop = self.loop
        app = loop.run_until_complete(self.create_app())
        app.on_startup.append(self.start_background_tasks)
        #app.on_cleanup.append(self.cleanup_background_tasks)
        web.run_app(app, host=self.host, port=self.port)
        # TODO gestionar el apagado y liberado de recursos

if __name__ == '__main__':
    
    s = ScraperServer(host='localhost', port=8080, accion_repo=accion_repo)
    s.run_app()
