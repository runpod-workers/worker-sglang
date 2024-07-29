import os
import runpod
from utils import JobInput
from engine import SGLangEngine, OpenAISGLangEngine

sglang_engine = SGLangEngine()
openai_sglang_engine = OpenAISGLangEngine(sglang_engine)

async def handler(job):
    job_input = JobInput(job["input"])
    engine = openai_sglang_engine if job_input.openai_route else sglang_engine
    results_generator = engine.generate(job_input)
    async for batch in results_generator:
        yield batch

runpod.serverless.start(
    {
        "handler": handler,
        "concurrency_modifier": lambda x: sglang_engine.max_concurrency,
        "return_aggregate_stream": True,
    }
)