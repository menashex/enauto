import time
import backoff
from unreliableapi import unreliable_api as unreliable_api

def on_backoff_handler(details):
    print(f"Retrying after exception: {details['exception']}")

def on_success_handler(details):
    print("Function succeeded without hitting max retries.")

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
        print(f"good data number {i+1}: ", data)
    except Exception as e:
        print(f"Error fetching data at iteration {i+1}: {e}")
        raise  # Let backoff handle the retry

if __name__ == "__main__":
    for i in range(5):
        sync_fetcher()
