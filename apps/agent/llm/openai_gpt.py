from .deepseek import DeepSeekClient


class OpenAIGPTClient(DeepSeekClient):
    provider = "openai"

    def __init__(self, api_key, base_url=None, model_name=None):
        base_url = base_url or "https://api.openai.com/v1"
        model_name = model_name or "gpt-4o"
        super().__init__(api_key, base_url, model_name)
