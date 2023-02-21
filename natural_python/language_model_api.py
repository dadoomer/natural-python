"""Language model API facade."""
import openai
from typing import Any
from typing import Generator


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
        ) -> Generator[list[str], None, None]:
    """Return completions for the given prompt."""
    stop_sequences = ['#']
    openai.api_key = api_key
    openai.api_base = api_base
    # OpenAI API limits to 128 samples per request
    if sample_n > 128:
        current_sample = 128
    else:
        current_sample = sample_n
    completions = openai.Completion.create(
        engine=engine_id,
        prompt=prompt,
        max_tokens=max_tokens,
        stream=False,
        n=current_sample,
        stop=stop_sequences,
        temperature=temperature,
    )
    candidates = [
        [l for l in c.text.split('\n') if len(l) > 0 and l not in stop_sequences]
        for c in completions["choices"]
    ]
    for candidate in candidates:
        yield candidate

    # Check if we need to ask for more samples
    remaining_samples = sample_n - current_sample
    if remaining_samples > 0:
        new_completions = get_completions(
            prompt=prompt,
            sample_n=remaining_samples,
            api_key=api_key,
            engine_id=engine_id,
            max_tokens=max_tokens,
            api_base=api_base,
            temperature=temperature,
        )
        for candidate in new_completions:
            yield candidate
