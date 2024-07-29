from sglang.srt.managers.io_struct import GenerateReqInput
from sglang.srt.managers.tokenizer_manager import TokenizerManager
from sglang.srt.server_args import ServerArgs
from sglang.srt.utils import allocate_init_ports

class ServerlessRuntime:
    def __init__(self, model_name):
        self.server_args = ServerArgs(
            model=model_name,
            tp_size=1,
            max_model_len=2048,
            # Add other arguments as needed
        )
        self.port_args = self._allocate_ports()
        self.tokenizer_manager = TokenizerManager(self.server_args, self.port_args)

    def _allocate_ports(self):
        self.server_args.port, self.server_args.additional_ports = allocate_init_ports(
            self.server_args.port,
            self.server_args.additional_ports,
            self.server_args.dp_size,
        )
        return self.server_args.additional_ports

    async def process_request(self, job_input):
        generate_req = GenerateReqInput(
            text=job_input.llm_input,
            sampling_params=job_input.sampling_params,
            stream=job_input.stream,
            max_batch_size=job_input.max_batch_size,
            request_id=job_input.request_id
        )
        async for response in self.tokenizer_manager.generate_request(generate_req):
            yield response

    def get_model_info(self):
        return {"model_path": self.server_args.model}