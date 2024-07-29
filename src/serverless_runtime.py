from sglang.srt.managers.io_struct import GenerateReqInput
from sglang.srt.managers.tokenizer_manager import TokenizerManager
from sglang.srt.server_args import ServerArgs, PortArgs
from sglang.srt.utils import allocate_init_ports

class ServerlessRuntime:
    def __init__(self, model_path):
        self.server_args = ServerArgs(
            model=model_path,
            tp_size=1,
            max_model_len=2048,
            # Add other arguments as needed
        )
        self._allocate_ports()
        self.tokenizer_manager = TokenizerManager(self.server_args, self.port_args)

    def _allocate_ports(self):
        self.server_args.port, additional_ports = allocate_init_ports(
            self.server_args.port,
            self.server_args.additional_ports,
            self.server_args.dp_size,
        )
        self.port_args = PortArgs(
            tokenizer_port=additional_ports[0],
            controller_port=additional_ports[1],
            detokenizer_port=additional_ports[2],
            nccl_ports=additional_ports[3:],
        )

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