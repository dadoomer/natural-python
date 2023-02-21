# natural-python

[Official Gitlab repo](https://gitlab.com/da_doomer/natural-python) | [Github mirror](https://github.com/dadoomer/natural-python) | [Blog post](https://iamleo.space/2023-02-20-llm-python-repl/)

This is a wrapper around the Python REPL which uses LLMs to search for code that matches your natural language specification and Python constraints.

Naturally, from a safety perspective the output of a LLM can only be assumed to be adversarial. Indeed, executing the output of an LLM is an inherently dangerous approach to implementing a REPL. Use at your own peril.

## Example

Hello world session: given this input

```python
>>> # Create a list with the days of the week, call it 'days'
>>> # finally:
+++ assert days[0] == 'Monday'
+++
```

the interpreter will write the following code:

```python
>>> days = [
>>>     'Monday',
>>>     'Tuesday',
>>>     'Wednesday',
>>>     'Thursday',
>>>     'Friday',
>>>     'Saturday',
>>> ]
>>> assert days[0] == 'Monday'
```

## Installation

`pip install --user git+https://gitlab.com/da_doomer/natural-python.git`

Then simply execute `natural-python --output my_script.py` in your shell (`--output` is an optional parameter).

The first time the interpreter is executed, it will ask for an API key. Currently, the interpreter supports GooseAI and OpenAI endpoints.

## Usage

Run `natural-python --help` to get the following:

```
usage: natural-python [-h] [--engine_id ENGINE_ID] [--completion_n COMPLETION_N] [--prediction_temperature PREDICTION_TEMPERATURE]
                      [--max_prediction_tokens MAX_PREDICTION_TOKENS] [--python_shell PYTHON_SHELL] [--show-engines] [--output OUTPUT]

Natural Python interpreter.

options:
  -h, --help            show this help message and exit
  --engine_id ENGINE_ID
                        Engine used for sampling.
  --completion_n COMPLETION_N
                        Engine used for sampling.
  --prediction_temperature PREDICTION_TEMPERATURE
                        Sampling temperature.
  --max_prediction_tokens MAX_PREDICTION_TOKENS
                        Maximum number of tokens in each candidate solution.
  --python_shell PYTHON_SHELL
                        Engine used for sampling.
  --show-engines        Display available engines.
  --output OUTPUT       Write the source code to a file at the end of the session.
```
