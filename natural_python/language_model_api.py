"""Language model API facade."""
import openai
from typing import Any


def get_engines(api_key: str, api_base: str) -> Any:
    openai.api_key = api_key
    openai.api_base = api_base
    engines = openai.Engine.list()
    return engines


def get_engine_ids(api_key: str, api_base: str) -> list[str]:
    openai.api_key = api_key
    openai.api_base = api_base
    engines = openai.Engine.list()
    engine_ids = [
        str(engine['id'])
        for engine in engines['data']
    ]
    return engine_ids


def get_completions(
        prompt: str,
        sample_n: int,
        api_key: str,
        engine_id: str,
        max_tokens: int,
        api_base: str,
        temperature: float,
        ) -> list[list[str]]:
    """Return completions for the given prompt."""
    stop_sequences = ['#']
    openai.api_key = api_key
    openai.api_base = api_base
    completions = openai.Completion.create(
        engine=engine_id,
        prompt=prompt,
        max_tokens=max_tokens,
        stream=False,
        n=sample_n,
        stop=stop_sequences,
        temperature=temperature,
    )
    candidates = [
        [l for l in c.text.split('\n') if len(l) > 0 and l not in stop_sequences]
        for c in completions["choices"]
    ]
    return candidates
