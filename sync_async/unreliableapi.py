import random
def unreliable_api():
    if random.random() < 0.3:
        raise Exception("API failed")
    return f"Data-{random.randint(1, 100)}"