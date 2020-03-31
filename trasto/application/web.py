import asyncio
from concurrent.futures import ThreadPoolExecutor

from aiohttp import web

from trasto.infrastructure.asyncio.repositories import (
    ResultadoAccionRepository, 
    TareaRepository,
    ComandoRepository)
from trasto.infrastructure.memory.repositories import EstadoDeHumorRepository

from trasto.infrastructure.asyncio.services import brain


async def get_service(request):

    return web.json_response({
        "service": "trastobrain", 
    })


async def new_task(request):
    comando_repo = ComandoRepository()
    
    return web.json_response({
        "msg": "solicitud recibida",
        "request": request
    })


class ScraperServer:

    def __init__(self, host, port, loop=None):

        self.host = host
        self.port = port

        self.loop = asyncio.get_event_loop() if loop is None else loop


    async def start_background_tasks(self, app):

        t_executor = ThreadPoolExecutor(
            max_workers=10
        )
        humor_repo = EstadoDeHumorRepository()
        tarea_repo = TareaRepository()
        resultado_repo = ResultadoAccionRepository()
        comando_repo = ComandoRepository()
        
        threads = await brain(
            thread_executor=t_executor,
            resultado_repo=resultado_repo,
            tarea_repo=tarea_repo,
            comando_repo=comando_repo,
            humor_repo=humor_repo)
        #completed, pending = await asyncio.wait(threads)
        for name, t in threads.items():
            app[name] = self.loop.create_task(t)


    async def cleanup_background_tasks(self, app):
        app['brain'].cancel()
        await app['brain']


    async def create_app(self):
        app = web.Application()
        app.router.add_get('/', get_service)
        app.router.add_post('/task', new_task)      
        return app


    def run_app(self):
        loop = self.loop
        app = loop.run_until_complete(self.create_app())
        app.on_startup.append(self.start_background_tasks)
        app.on_cleanup.append(self.cleanup_background_tasks)
        web.run_app(app, host=self.host, port=self.port)
        # TODO gestionar el apagado y liberado de recursos

if __name__ == '__main__':
    
    s = ScraperServer(host='localhost', port=8080)
    s.run_app()