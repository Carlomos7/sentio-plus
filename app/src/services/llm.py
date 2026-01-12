"""LLM client service using LangChain."""

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from src.config.logging import get_logger
from src.config.settings import LLMProvider

logger = get_logger(__name__)


class LLMClient:
    """Unified LLM client wrapping LangChain models."""

    def __init__(
        self,
        provider: LLMProvider,
        model: str,
        base_url: str | None = None,
        api_key: str = "",
        temperature: float = 0.1,
        max_tokens: int = 1000,
        aws_region: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
    ):
        """Initialize LLM client.

        Args:
            provider: LLM provider (openai or bedrock).
            model: Model name/ID.
            base_url: API base URL (for OpenAI-compatible).
            api_key: API key.
            temperature: Sampling temperature.
            max_tokens: Max tokens in response.
            aws_region: AWS region (for Bedrock).
        """
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.aws_region = aws_region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

        self.llm = self._create_llm(
            provider=provider,
            model=model,
            base_url=base_url,
            api_key=api_key,
        )

        logger.info(f"LLM client initialized: {provider.value} / {model}")

    def _create_llm(
        self,
        provider: LLMProvider,
        model: str,
        base_url: str | None,
        api_key: str,
    ) -> BaseChatModel:
        """Create the underlying LangChain model."""
        if provider == LLMProvider.BEDROCK:
            import boto3
            from langchain_aws import ChatBedrock

            if not self.aws_access_key_id or not self.aws_secret_access_key:
                raise ValueError("AWS credentials are required for Bedrock provider.")

            client = boto3.client(
                "bedrock-runtime",
                region_name=self.aws_region or "us-west-2",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
            return ChatBedrock(
                model_id=model,
                client=client,
                model_kwargs={
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                },
            )
        else:
            from langchain_openai import ChatOpenAI

            if not base_url:
                raise ValueError("Base URL is required for OpenAI-compatible provider.")
            
            return ChatOpenAI(
                base_url=base_url,
                model=model,
                api_key=api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

    def invoke(self, prompt: str) -> str:
        """Invoke LLM with a simple prompt.

        Args:
            prompt: The prompt string.

        Returns:
            Response content.
        """
        response = self.llm.invoke(prompt)
        return response.content

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        """Generate response with optional system prompt.

        Args:
            prompt: User prompt.
            system_prompt: Optional system instructions.

        Returns:
            Generated text.
        """
        messages = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        messages.append(HumanMessage(content=prompt))

        response = self.llm.invoke(messages)
        return response.content

    def get_model_info(self) -> dict[str, Any]:
        """Get model info."""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
