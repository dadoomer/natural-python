# natural-python

Natural Python is an intermediary between you (who speaks in natural language)
and the computer (who speaks Python).

More concretely, this is a wrapper around the Python REPL which uses LLMs to search for code that matches your natural language specification and Python constraints.

## Example

Hello world session:

```python
Natural Python 0.1.0 on Python 3.10.6
Language model engine ID: gpt-neo-125m
Type exit to exit.
Type restart to erase your current instruction.
Type help for more information.
>>> # Create a list with the days of the week, call it 'days'
>>> # finally:
+++ assert days[0] == 'Monday'
+++
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
