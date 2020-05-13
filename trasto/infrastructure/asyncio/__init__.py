import asyncio
import queue


#class to provide queue (sync or asyc morph)
class QueueMorph(queue.Queue):
    def __init__(self, maxsize=0, timeout=0.01):
        super().__init__(maxsize)
        self.timeout=timeout

    async def aget(self):
        while True:
            try:
                return self.get_nowait()
            except queue.Empty:
                await asyncio.sleep(self.timeout)
            except Exception as e:
                raise e

    async def aput(self,data):
        while True:
            try:
                return self.put_nowait(data)
            except queue.Full:
                
                await asyncio.sleep(self.timeout)
            except Exception as e:
                raise e
