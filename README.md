<div align="center">

<h1>Preview | SgLang Worker</h1>

🚀 | SgLang runtime inference worker.
</div>

## 📖 | Getting Started

1. Clone this repository.
2. Build a docker image - ```docker build -t <your_username>:worker-sglang:v1 .```
3. ```docker push <your_username>:worker-sglang:v1```


***Once you have built the Docker image and deployed the endpoint, you can use the code below to interact with the endpoint***: 

```
import runpod

runpod.api_key = "your_runpod_api_key_found_under_settings"

# Initialize the endpoint
endpoint = runpod.Endpoint("ENDPOINT_ID")

# Run the endpoint with input data
run_request = endpoint.run({"your_model_input_key": "your_model_input_value"})

# Check the status of the endpoint run request
print(run_request.status())

# Get the output of the endpoint run request, blocking until the run is complete
print(run_request.output()) 
```









## 💡 | Note: 
This is an initial and preview phase of the worker's development. Future updates will include more configurability and compatibility with OpenAI, which is currently being developed.

