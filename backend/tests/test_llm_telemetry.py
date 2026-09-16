import json
import logging

from langchain_core.messages import AIMessage

from app.config import settings
from app.llm_versions import LLMVersion
from app.services import llm


class ModelWithUsage:
    def invoke(self, messages):
        return AIMessage(
            content="hello",
            response_metadata={
                "token_usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 25,
                    "total_tokens": 125,
                }
            },
        )


def test_invoke_logs_versioned_usage_and_cost(caplog):
    version = LLMVersion(
        provider="openai",
        model="gpt-4o-mini",
        prompt_name="drink-assistant-system",
        prompt_version="9.9.9",
        prompt_hash="deadbeefcafe",
    )
    with caplog.at_level(logging.INFO, logger=llm.__name__):
        result = llm.invoke(ModelWithUsage(), [], version)

    assert result.content == "hello"
    event = json.loads(caplog.records[-1].message)
    assert event["event"] == "llm_invocation"
    assert event["success"] is True
    assert event["prompt_version"] == "9.9.9"
    assert event["prompt_hash"] == "deadbeefcafe"
    assert event["input_tokens"] == 100
    assert event["output_tokens"] == 25
    assert result.usage.input_tokens == 100
    assert result.usage.output_tokens == 25
    expected_cost = round(
        (100 / 1_000_000) * settings.llm_input_cost_per_million
        + (25 / 1_000_000) * settings.llm_output_cost_per_million,
        8,
    )
    assert event["estimated_cost_usd"] == expected_cost
    assert result.usage.estimated_cost_usd == expected_cost
