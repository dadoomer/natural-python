from importlib.metadata import version
from platform import python_version
from enum import Enum
from enum import auto
from pathlib import Path
import argparse
from natural_python import language_model_api
from natural_python import interpreter
from pathlib import Path
import shutil
import json
from rich.markdown import Markdown
from rich.console import Console
import tempfile


# Is this a security risk?
api_file = Path(__file__).parent/'api.json'

help_keyword = "help"
exit_keyword = "exit"
constraint_keyword = "finally:"
restart_keyword = "restart"
python_keyword = "python"
keywords = [
    help_keyword,
    exit_keyword,
    constraint_keyword,
    restart_keyword,
    python_keyword,
]


def print_help_message():
    help_message = Markdown(
        f"""DO NOT ATTEMPT, EVER, TO EXECUTE CODE THAT MODIFIES YOUR FILESYSTEM. INTERACTING WITH THIS TOOL IS EXTREMELY RISKY, DO SO AT YOUR OWN PERIL.

In Natural Python, you primarily express intent with natural language.

- A block of commented lines represents your intent.
- Everything in a block represents a single instruction.
- You can constrain the execution by ending the comment block with '{constraint_keyword}', followed by a line break and Python code that has to run successfully after executing your instruction.

Once you enter an empty line, your intent will be executed by the computer by finding Python code that runs without exceptions.

The following illustrates these concepts. Try it out!

```py
>>> # Create a list with the days of the week, call it 'days'
>>> # {constraint_keyword}"
+++ assert days[0] == 'Monday'
+++```
"""
    )
    console = Console()
    console.print(help_message)

python_shell_candidates = [
    "python3",
    "python",
]


class State(Enum):
    reading_instruction = auto()
    reading_constraint = auto()
    reading_raw_code = auto()
    restarting_instruction_reading = auto()
    ready_to_execute = auto()


class ParseException(Exception):
    """Raised when the user provides an input of invalid format."""
    def __init__(self, cause: str):
        self.cause = cause


def print_start_message(
        engine_id: str,
        ):
    start_message = "\n".join([
        f"Natural Python {version('natural_python')} on Python {python_version()}",
        f"Language model engine ID: {engine_id}",
        f"Type {exit_keyword} to exit.",
        f"Type {restart_keyword} to erase your current instruction.",
        f"Type {python_keyword} to bypass the Natural Python interpreter and write raw Python to the stream.",
        f"Type {help_keyword} for more information.",
        f"Run the interpreter with --help for more options.",
    ])
    print(start_message)


def repl(
        engine_id: str,
        api_key: str,
        api_base: str,
        max_sample_tokens: int,
        sample_n: int,
        sample_temperature: float,
        python_shell: str,
        ) -> list[str]:
    """Read-eval-print loop. Returns the executed python code."""
    print_start_message(
        engine_id=engine_id,
    )
    keep_interpreting = True
    current_instruction = list()
    current_constraint = list()
    current_python_code = list()

    state = State.reading_instruction

    while keep_interpreting:
        # State machine loop
        if state is State.restarting_instruction_reading:
            current_instruction = list()
            current_constraint = list()
            state = State.reading_instruction
        elif state is State.ready_to_execute:
            program = interpreter.NaturalProgram(
                instruction=current_instruction,
                constraint=current_constraint,
            )
            # Execute natural program
            try:
                new_python_code, output = interpreter.execute_natural_program(
                    program=program,
                    current_python_code=current_python_code,
                    sample_n=sample_n,
                    python_shell=python_shell,
                    engine_id=engine_id,
                    api_key=api_key,
                    api_base=api_base,
                    max_sample_tokens=max_sample_tokens,
                    sample_temperature=sample_temperature,
                )

                # Print executed code
                print("\n".join(['>>> '+l for l in new_python_code]))
                print(output)

                # Update current python code
                commented_instructions = ['# '+l for l in program.instruction]
                current_python_code.extend([
                    *commented_instructions,
                    *new_python_code,
                ])
            except interpreter.NaturalInterpreterError:
                print("ERROR: Failed to execute code with budget. Maybe try more detailed instructions?")

            state = State.restarting_instruction_reading
        else:
            # Read user input
            if state is State.reading_instruction:
                prompt = ">>> # "
            elif state is State.reading_raw_code:
                prompt = ">>> "
            else:  # state is State.reading_constraint
                prompt = "+++ "

            # Parse input
            try:
                user_input = str(input(prompt))

                # Sanitize user input
                user_input = user_input.strip()
                if user_input in keywords:
                    # User input is a keyword
                    if user_input == help_keyword:
                        # Help
                        print_help_message()
                    elif user_input == exit_keyword:
                        keep_interpreting = False
                    elif user_input == constraint_keyword:
                        # Constraint reading can only happen when reading instructions
                        if state != State.reading_instruction:
                            raise ParseException(f"You can only use '{constraint_keyword}' while providing instructions!")
                        # Start constraint reading
                        state = State.reading_constraint
                    elif user_input == restart_keyword:
                        state = State.restarting_instruction_reading
                    elif user_input == python_keyword:
                        if len(current_instruction) != 0 or len(current_constraint) != 0:
                            raise ParseException(f"You can only use '{python_keyword}' before providing any instructions or constraints!")
                        state = State.reading_raw_code
                elif len(user_input) == 0:
                    # Block end
                    # If the block is empty, restart reading
                    if len(current_instruction) == 0 and len(current_constraint) == 0:
                        state = State.restarting_instruction_reading
                    else:
                        state = State.ready_to_execute
                elif state is State.reading_instruction:
                    # Continue reading instructions
                    current_instruction.append(user_input)
                elif state is State.reading_constraint:
                    # Continue reading instructions
                    current_constraint.append(user_input)
                elif state is State.reading_raw_code:
                    current_python_code.append(user_input)
                else:
                    # This should never happen
                    raise ParseException("You did not format your input correctly... try again...")
            except EOFError:
                keep_interpreting = False
            except ParseException as e:
                print(e.cause)
                state = State.restarting_instruction_reading
    return current_python_code


def main():
    # Check if API key is present
    try:
        with open(api_file, "rt") as fp:
            api_config = json.load(fp)
    except FileNotFoundError:
        print("Initial configuration. You will only have to do this once.")
        print("Get an API key at https://goose.ai/dashboard/apikeys.")
        api_base = input("API base (e.g. https://api.goose.ai/v1, https://api.openai.com/v1): ")
        api_key = input("API key: ")
        api_config = dict(
            api_key=api_key,
            api_base=api_base,
        )
        with open(api_file, "wt") as fp:
            json.dump(api_config, fp)
        print(f"Wrote {api_file}")

    # Parse arguments
    parser = argparse.ArgumentParser(
            description='Natural Python interpreter.',
            epilog=f'The API configuration file is {api_file}. Delete this file if you want to change keys',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    parser.add_argument(
        '--engine-id',
        help="Language model engine used for sampling.",
        type=str,
        default="gpt-neo-125m",
    )
    parser.add_argument(
        '--sample-n',
        help="Number of samples drawn from the language model when executing an instruction.",
        type=int,
        default=10,
    )
    parser.add_argument(
        '--sample-temperature',
        help="Sampling temperature.",
        type=float,
        default=0.2,
    )
    parser.add_argument(
        '--max-sample-tokens',
        help="Maximum number of tokens in each sample.",
        type=int,
        default=100,
    )
    parser.add_argument(
        '--python-shell',
        help="Command used to spawn a Python interpreter. If None, a best guess will be made.",
        type=str,
    )
    parser.add_argument(
        '--show-engines',
        help="Display available language model engines.",
        action='store_true',
    )
    parser.add_argument(
        '--output',
        help="Output file to write session script. If None, output will be written to a temporary file.",
        type=Path,
        default=None,
    )
    args = parser.parse_args()

    # Handle arguments
    api_key = api_config['api_key']
    api_base = api_config['api_base']
    if args.show_engines:
        engines = language_model_api.get_engines(
            api_key=api_key,
            api_base=api_base,
        )
        print(engines)
    else:
        # Check that the engine is valid
        engine_id = args.engine_id
        if engine_id not in language_model_api.get_engine_ids(api_key, api_base):
            raise ValueError(f'Invalid engine {engine_id}')

        # Decide a python shell
        if args.python_shell is not None:
            python_shell: (None|str) = args.python_shell
        else:
            python_shell = None
            for python_shell_candidate in python_shell_candidates:
                if shutil.which(python_shell_candidate) is not None:
                    python_shell = python_shell_candidate
        if python_shell is None or shutil.which(python_shell) is None:
            raise ValueError(f"Invalid Python shell {python_shell}")

        # Run the REPL
        code = repl(
            engine_id=engine_id,
            api_key=api_key,
            sample_n=args.sample_n,
            python_shell=python_shell,
            api_base=api_base,
            max_sample_tokens=args.max_sample_tokens,
            sample_temperature=args.sample_temperature,
        )

        # Write interaction if requested
        if args.output is not None:
            output_file = args.output
        else:
            output_file = Path(tempfile.NamedTemporaryFile(
                'wt',
                delete=False,
                prefix='natural-python',
                suffix='.py',
            ).name)
        with open(output_file, "wt") as fp:
            fp.write("\n".join(code))
        print(f"Session log script written to {output_file}")
