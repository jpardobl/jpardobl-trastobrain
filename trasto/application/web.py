import asyncio

from aiohttp import web


class ScraperServer:

    def __init__(self, host, port, loop=None):

        self.host = host
        self.port = port

        self.loop = asyncio.get_event_loop() if loop is None else loop


    async def start_background_tasks(self, app):

        t_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=int(config.args.connect_thread_max_workers) + 2 # Para permitir el monitor y la persistencia de estado
        )

        app['manager'] = self.loop.create_task(manager(t_executor))

    async def cleanup_background_tasks(self, app):
        app['manager'].cancel()
        for _, data in connectors.items():
            data['tasks'][0].cancel()
        for t in asyncio.Task.all_tasks():
            t.cancel()
        await app['manager']

    async def create_app(self):
        app = web.Application()
        app.router.add_get('/', get_service)
        
        app.router.add_get('/connectors', get_connectors)
        app.router.add_get('/offsets', get_offsets)
        app.router.add_get('/connectors/{name}/status', get_connector_status)
        app.router.add_get('/connectors/{name}', get_connector_status)
        app.router.add_get('/connectors/{name}/tasks/0/status', get_task_status)
        app.router.add_get('/connectors/{name}/tasks/1/status', get_task_status)
        
        """
        POST /connectors
        {
            
            "name": "nombre del connector",
            "config": {
                
                "sistema": "Sistema que origina los datos a ingestar",
                "datalake": "Datalake donde se deben dejar los datos",
                "estructura": "nombre de la estructura de datos. Asi se vera en el datadictionary",
                "conector": {
                    ["nombre_funcion": {params}]                     
                }                
                "funciones": ["lista de funciones a ejecutar"]
            }
        }
        """
        app.router.add_post('/connectors', new_connector)        
        app.router.add_delete('/connectors/{name}', delete_connector)        
        app.router.add_post('/connectors/{name}/tasks/0/restart', restart_task)
        app.router.add_post('/connectors/{name}/restart', restart_task)        

        return app

    def run_app(self):

        loop = self.loop
        app = loop.run_until_complete(self.create_app())
        app.on_startup.append(self.start_background_tasks)
        app.on_cleanup.append(self.cleanup_background_tasks)
        web.run_app(app, host=self.host, port=self.port)
        # TODO gestionar el apagado y liberado de recursos
