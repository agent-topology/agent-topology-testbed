"""T1's complete input: two deterministic activities and two workflow definitions.

Only decorators execute during inspection; no workflow/activity body is called.
Explicit Temporal type names intentionally differ from Python names.
"""

from datetime import timedelta

from temporalio import activity, workflow

BODIES_ENTERED = []


@activity.defn(name="t1.a")
async def activity_a(value: str) -> str:
    BODIES_ENTERED.append("activity_a")
    return "a:" + value


@activity.defn(name="t1.b")
async def activity_b(value: str) -> str:
    BODIES_ENTERED.append("activity_b")
    return "b:" + value


@workflow.defn(name="t1.linear")
class LinearWorkflow:
    @workflow.run
    async def run(self, value: str) -> str:
        BODIES_ENTERED.append("LinearWorkflow.run")
        result = await workflow.execute_activity(
            activity_a, value, start_to_close_timeout=timedelta(seconds=5)
        )
        return await workflow.execute_activity(
            activity_b, result, start_to_close_timeout=timedelta(seconds=5)
        )


@workflow.defn(name="t1.choice")
class ChoiceWorkflow:
    @workflow.run
    async def run(self, value: str) -> str:
        BODIES_ENTERED.append("ChoiceWorkflow.run")
        if value == "a":
            return await workflow.execute_activity(
                activity_a, value, start_to_close_timeout=timedelta(seconds=5)
            )
        return await workflow.execute_activity(
            activity_b, value, start_to_close_timeout=timedelta(seconds=5)
        )
