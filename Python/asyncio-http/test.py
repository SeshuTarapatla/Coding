from asyncio import Lock, Semaphore, gather, run
from pathlib import Path
from time import time
from typing import Literal
from aiohttp import ClientSession
from requests import get
from vars import DOG_API

class DOG:
    def __init__(self) -> None:
        pass

    def fetch_image(self) -> None:
        self.response: dict[Literal["message", "status"], str] = get(DOG_API.RANDOM).json()
        self.image_url = self.response.get("message", "")
        self.status = self.response["status"]
        self.image = get(self.image_url).content
        self.output = Path("cache") / Path(self.image_url).relative_to(DOG_API.IMAGE)
        self.output.parent.mkdir(exist_ok=True, parents=True)
        self.output.write_bytes(self.image)
    
    async def fetch_image2(self, session: ClientSession) -> None:
        async with session.get(DOG_API.RANDOM) as response:
            self.response: dict[Literal["message", "status"], str] = await response.json()
            self.image_url = self.response["message"]
            self.status = self.response["status"]
        async with session.get(self.image_url) as data:
            self.image = await data.content.read()
            self.output = Path("cache") / Path(self.image_url).relative_to(DOG_API.IMAGE)
            self.output.parent.mkdir(exist_ok=True, parents=True)
            self.output.write_bytes(self.image)

def process_batch(batch: list[DOG]) -> None:
    total = len(batch)

    def process_current(index: int, object: DOG) -> None:
        object.fetch_image()
        print(f"{(index/total):.2%} >> {object.image_url}: {object.status}")
    
    [process_current(i, dog) for i, dog in enumerate(batch, start=1)]

async def process_batch_async(batch: list[DOG]) -> None:
    total: int = len(batch)
    counter: int = 0
    counter_lock = Lock()
    semaphore = Semaphore(50)

    async with ClientSession() as session:
        async def process_current(object: DOG) -> None:
            nonlocal counter
            async with semaphore:
                await object.fetch_image2(session)
                async with counter_lock:
                    counter += 1
                    print(f"{(counter/total):.2%} >> {object.image_url}: {object.status}")
        tasks = [process_current(dog) for dog in batch]
        await gather(*tasks)


if __name__ == "__main__":
    dogs = [DOG() for _ in range(100)]

    print("SYNCHRONOUS MODE:")
    start = time()
    process_batch(dogs)
    sync_mode = time() - start
    print('\n') 
    
    print("ASYNCHRONOUS MODE:")
    start = time()
    run(process_batch_async(dogs))
    async_mode = time() - start
    print('\n')

    print(f"Total time taken -> Sync: {sync_mode} | Async: {async_mode}")
    factor = sync_mode/async_mode
    print(f"Asynchronous mode is {factor:.4f} times faster 🚀 [{factor:.2%}]")
