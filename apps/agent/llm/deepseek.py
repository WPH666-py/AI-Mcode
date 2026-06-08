from .base import BaseLLMClient
from openai import AsyncOpenAI, OpenAI
import asyncio


class DeepSeekClient(BaseLLMClient):
    provider = "deepseek"

    def __init__(self, api_key, base_url=None, model_name=None):
        super().__init__(api_key, base_url, model_name)
        self.base_url = base_url or "https://api.deepseek.com/v1"
        self.model_name = model_name or "deepseek-chat"
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=self.base_url, timeout=None)
        self.sync_client = OpenAI(api_key=api_key, base_url=self.base_url, timeout=None)

    async def chat(self, prompt, system_prompt=None, stream=False):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if stream:
            return await self._chat_stream(messages)
        else:
            response = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content

    async def _chat_stream(self, messages):
        stream = await self.async_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def chat_sync(self, prompt, system_prompt=None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = self.sync_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
