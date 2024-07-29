from typing import Dict, Any, Optional

class JobInput:
    def __init__(self, input_data: Dict[str, Any]):
        self.openai_route: Optional[str] = input_data.get('openai_route')
        self.openai_input: Optional[Dict[str, Any]] = input_data.get('openai_input')
        self.llm_input: Any = input_data.get('llm_input')
        self.sampling_params: Dict[str, Any] = input_data.get('sampling_params', {})
        self.max_batch_size: Optional[int] = input_data.get('max_batch_size')
        self.stream: bool = input_data.get('stream', False)
        self.apply_chat_template: bool = input_data.get('apply_chat_template', False)
        self.request_id: Optional[str] = input_data.get('request_id')
        self.batch_size_growth_factor: Optional[float] = input_data.get('batch_size_growth_factor')
        self.min_batch_size: Optional[int] = input_data.get('min_batch_size')