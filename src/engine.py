import os
from sglang import Runtime

MODEL_PATH = os.environ.get("MODEL_PATH", "meta-llama/Llama-2-7b-chat-hf")

class SGLangEngine:
    def __init__(self):
        self.runtime = Runtime(model_path=MODEL_PATH)
        self.tokenizer = self.runtime.get_tokenizer()

    async def generate(self, prompt, sampling_params):
        messages = [
            {
                "role": "system",
                "content": "You will be given question answer tasks.",
            },
            {"role": "user", "content": prompt},
        ]
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        
        result = []
        stream = self.runtime.add_request(prompt, sampling_params)
        async for output in stream:
            result.append(output)
        
        return "".join(result)

    def shutdown(self):
        self.runtime.shutdown()