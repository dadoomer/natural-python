# natural-python

[Official Gitlab repo](https://gitlab.com/da_doomer/natural-python) | [Github mirror](https://github.com/dadoomer/natural-python)

Natural Python is an intermediary between you (who speaks in natural language)
and the computer (who speaks Python).

More concretely, this is a wrapper around the Python REPL which uses LLMs to search for code that matches your natural language specification and Python constraints.

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
