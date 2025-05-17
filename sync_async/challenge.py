import time
import backoff
import asyncio
from unreliableapi import unreliable_api as unreliable_api

def on_backoff_handler(details):
    print(f"Retrying after exception: {details['exception']}")

def on_success_handler(details):
    print("Function succeeded without hitting max retries.")


### Synchronous Fetcher with liean backoff
def linear_backoff():
    i = 1
    while True:
        yield i # yield remembers the value and resumes on next call
        i += 1

@backoff.on_exception(
    linear_backoff, # alternative to backoff.expo which is exponential
    Exception,
    max_tries=20,
    on_backoff=on_backoff_handler,
    #on_success=on_success_handler
)
def sync_fetcher():
    try:
        data = unreliable_api()
        print(f"(sync) good data number {i+1}: ", data)
    except Exception as e:
        print(f"(sync) Error fetching data at iteration {i+1}: {e}")
        raise  # Let backoff handle the retry



### async fetcher with exponential backoff
@backoff.on_exception(
    backoff.expo, # exponential
    Exception,
    max_tries=20,
    on_backoff=on_backoff_handler,
    #on_success=on_success_handler
)
async def async_fetcher():
    try:
        data = unreliable_api()
        print(f"(a-sync) good data: ", data)
    except Exception as e:
        print(f"(a-sync) Error fetching data: {e}")
        raise  # Let backoff handle the retry

async def main_async():
    await asyncio.gather(async_fetcher(), async_fetcher(), async_fetcher(), async_fetcher(), async_fetcher())


if __name__ == "__main__":
    s = time.perf_counter()
    asyncio.run(main_async())
    for i in range(5):
        sync_fetcher()
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
