import os
import json
import asyncio
from typing import Dict, Any, AsyncGenerator
from dotenv import load_dotenv

from sglang.srt.managers.io_struct import GenerateReqInput
from sglang.srt.openai_api.adapter import v1_chat_completions, v1_completions
from sglang.srt.openai_api.protocol import ChatCompletionRequest, CompletionRequest, ErrorResponse

from serverless_runtime import ServerlessRuntime

load_dotenv()  # For local development

class SGLangEngine:
    def __init__(self):
        self.runtime = ServerlessRuntime(
            model_path=os.getenv("MODEL_NAME")
            # Add other necessary arguments here
        )
        self.max_concurrency = int(os.getenv("MAX_CONCURRENCY", 10))

    async def generate(self, job_input):
        try:
            async for batch in self.runtime.process_request(job_input):
                yield batch
        except Exception as e:
            yield {"error": self._create_error_response(str(e))}

    def _create_error_response(self, message: str) -> Dict[str, Any]:
        return ErrorResponse(message=message, type="invalid_request_error").model_dump()

class OpenAISGLangEngine:
    def __init__(self, sglang_engine: SGLangEngine):
        self.sglang_engine = sglang_engine
        self.served_model_name = os.getenv("OPENAI_SERVED_MODEL_NAME_OVERRIDE") or os.getenv("MODEL_NAME")
        self.response_role = os.getenv("OPENAI_RESPONSE_ROLE") or "assistant"
        self.raw_openai_output = bool(int(os.getenv("RAW_OPENAI_OUTPUT", 1)))

    async def generate(self, job_input) -> AsyncGenerator[Dict[str, Any], None]:
        if job_input.openai_route == "/v1/models":
            yield await self._handle_model_request()
        elif job_input.openai_route in ["/v1/chat/completions", "/v1/completions"]:
            async for response in self._handle_chat_or_completion_request(job_input):
                yield response
        else:
            yield self._create_error_response("Invalid route")

    async def _handle_model_request(self):
        model = {
            "id": self.served_model_name,
            "object": "model",
            "created": 1686935002,
            "owned_by": "organization-owner",
        }
        return {"data": [model], "object": "list"}

    async def _handle_chat_or_completion_request(self, job_input) -> AsyncGenerator[Dict[str, Any], None]:
        if job_input.openai_route == "/v1/chat/completions":
            request_class = ChatCompletionRequest
            generator_function = v1_chat_completions
        elif job_input.openai_route == "/v1/completions":
            request_class = CompletionRequest
            generator_function = v1_completions

        try:
            request = request_class(**job_input.openai_input)
        except Exception as e:
            yield self._create_error_response(str(e))
            return

        mock_request = MockRequest(request.model_dump())
        response_generator = await generator_function(self.sglang_engine.runtime.tokenizer_manager, mock_request)

        if not job_input.openai_input.get("stream"):
            yield json.loads(response_generator.body)
        else:
            async for chunk in self._stream_response(response_generator):
                yield chunk

    async def _stream_response(self, response_generator):
        batch = []
        async for chunk in response_generator.body_iterator:
            if self.raw_openai_output:
                yield chunk
            else:
                data = json.loads(chunk.decode('utf-8').removeprefix("data: ").rstrip("\n\n"))
                if data != "[DONE]":
                    batch.append(data)
                    if len(batch) >= 5:  # You can adjust this batch size
                        yield batch
                        batch = []
        if batch:
            yield batch

    def _create_error_response(self, message: str) -> Dict[str, Any]:
        return ErrorResponse(message=message, type="invalid_request_error").model_dump()

class MockRequest:
    def __init__(self, json_data):
        self.json_data = json_data

    async def json(self):
        return self.json_data