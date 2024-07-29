import runpod
import asyncio
import logging
from engine import SGLangEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the SGLangEngine globally
engine = SGLangEngine()
logger.info("--- SGLang Engine ready ---")

async def handler(job):
    try:
        job_input = job["input"]
        prompt = job_input.get("prompt", "")
        sampling_params = job_input.get("sampling_params", {"max_new_tokens": 128})
        
        response = await engine.generate(prompt, sampling_params)
        
        return {"generated_text": response}
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}")
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})