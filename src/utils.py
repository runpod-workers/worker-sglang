import json
import os 

def format_chunk(chunk):
    chunk = chunk.strip()
    if chunk.startswith('data: '):
        chunk = chunk[6:]  # Remove 'data: ' prefix
    
    if chunk == '[DONE]':
        return f"data: {chunk}\n\n"
    
    try:
        # Try to parse as JSON
        data = json.loads(chunk)
        formatted_json = json.dumps(data, indent=4)
        formatted_lines = [f"data: {line}" for line in formatted_json.split('\n')]
        return '\n'.join(formatted_lines) + '\n\n'
    except json.JSONDecodeError:
        # If it's not valid JSON, return as plain text
        return f"data: {chunk}\n\n"
    
def process_response(response):
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            yield format_chunk(decoded_line)

def topath(raw: str) -> str:
    raw = raw.strip()
    if ":" in raw:
            model, branch = raw.rsplit(":", maxsplit=1)
    else:
            model, branch = raw, "main"
    if "/" not in model:
        raise ValueError(f"invalid model: expected one in the form user/model[:path], but got {model}")
    user, model = model.rsplit("/", maxsplit=1)
    return os.path.join("/runpod", "cache", "models", user, model, branch)


def modelpaths() -> list[str]:
    raw = os.environ.get("RUNPOD_HUGGINGFACE_MODEL")
    if not raw:
        return []
    return [topath(m) for m in raw.split(",")]