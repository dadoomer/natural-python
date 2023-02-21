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

Then simply execute `natural-python` in your shell.
