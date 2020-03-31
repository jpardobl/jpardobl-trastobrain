
import asyncio

from trasto.infrastructure.asyncio.repositories import (ResultadoAccionRepository, TareaRepository )
from trasto.infrastructure.memory.repositories import (ComandoRepository, EstadoDeHumorRepository )

from concurrent.futures import ThreadPoolExecutor

from trasto.infrastructure.asyncio.services import brain


        
async def main():
    t_executor = ThreadPoolExecutor(
        max_workers=10
    )
    humor_repo = EstadoDeHumorRepository()
    tarea_repo = TareaRepository()
    resultado_repo = ResultadoAccionRepository()
    comando_repo = ComandoRepository()

    event_loop = asyncio.get_event_loop()

    
    threads = await brain(
        thread_executor=t_executor,
        resultado_repo=resultado_repo,
        tarea_repo=tarea_repo,
        comando_repo=comando_repo,
        humor_repo=humor_repo)

    
    completed, pending = await asyncio.wait(threads)

    print("Arrancado el brain")


    
            
asyncio.run(main())
