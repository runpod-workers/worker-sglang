import asyncio
import unittest

from utils import async_process_response


class FakeContent:
    def __init__(self, lines):
        self._lines = lines

    def __aiter__(self):
        self._iterator = iter(self._lines)
        return self

    async def __anext__(self):
        try:
            return next(self._iterator)
        except StopIteration as error:
            raise StopAsyncIteration from error


class FakeResponse:
    def __init__(self, status=200, lines=(), body=""):
        self.status = status
        self.content = FakeContent(lines)
        self._body = body

    async def text(self):
        return self._body


async def collect_response(response, is_stream=False, route="/v1/chat/completions"):
    return [
        item
        async for item in async_process_response(response, is_stream, route)
    ]


class ResponseProcessingTests(unittest.TestCase):
    def test_non_success_response_yields_structured_error(self):
        response = FakeResponse(status=500, body="boom")

        result = asyncio.run(collect_response(response))

        self.assertEqual(
            result,
            [
                {
                    "error": (
                        "Request to /v1/chat/completions failed with status 500"
                    ),
                    "details": "boom",
                }
            ],
        )

    def test_non_stream_response_yields_non_empty_decoded_lines(self):
        response = FakeResponse(lines=[b'{"id":"one"}\n', b"\n", b'{"id":"two"}\n'])

        result = asyncio.run(collect_response(response))

        self.assertEqual(result, ['{"id":"one"}', '{"id":"two"}'])

    def test_stream_response_formats_sse_and_done_marker(self):
        response = FakeResponse(
            lines=[b'data: {"token":"hello"}\n', b"data: [DONE]\n"]
        )

        result = asyncio.run(collect_response(response, is_stream=True))

        self.assertEqual(
            result,
            ['data: {"token": "hello"}\n\n', "data: [DONE]\n\n"],
        )


if __name__ == "__main__":
    unittest.main()
