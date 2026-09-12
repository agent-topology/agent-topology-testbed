"""Minimal P8 input; body entry is instrumentation, not an extracted edge."""
from prefect import flow, task
from prefect.cache_policies import NO_CACHE

BODIES_ENTERED = []


@task(name="p8.a", version="p8-v1", cache_policy=NO_CACHE, persist_result=False)
def task_a():
    BODIES_ENTERED.append("a")
    return ["a"]


@task(name="p8.b", version="p8-v1", cache_policy=NO_CACHE, persist_result=False)
def task_b(value):
    BODIES_ENTERED.append("b")
    return value[0] + "b"


@flow(name="p8.linear", version="p8-v1", persist_result=False)
def linear():
    first = task_a(return_state=True)
    return [task_b(first)]


@flow(name="p8.loop", version="p8-v1", persist_result=False)
def loop(count: int):
    results = []
    for _ in range(count):
        first = task_a(return_state=True)
        results.append(task_b(first))
    return results
