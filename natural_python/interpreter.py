"""Natural Python semantics."""
from dataclasses import dataclass
from natural_python.language_model_api import get_completions
import tempfile
import subprocess
import shlex


@dataclass
class NaturalProgram:
    """A natural program is any combination of an instruction and a constraint."""
    instruction: list[str]
    """Natural language description of desired transformation of the program
    state."""
    constraint: list[str]
    """Python code which has to be successfully executed after executing the
    instruction. Most often, an assertion like `assert my_list[0] <
    my_list[1]`."""


class NaturalInterpreterError(Exception):
    """Raised when the interpreter fails to find Python code that does not
    crash the program."""
    pass


class PythonInterpreterError(Exception):
    """Raised when a Python interpreter exits with error status."""
    pass


def get_prompt(
        current_code: list[str],
        program: NaturalProgram,
        ) -> str:
    """Get a prompt for sampling implementations of the given program, assuming
    we have executed some Python `current_code`."""
    # If this is the first code we will execute, inject a short prefix
    # to increase likelihood of Python programs in the language model
    if len(current_code) == 0:
        injected_prompt = [
            "# Let's write a Python script to solve the problem",
            "import argparse",
            "",
        ]
    else:
        injected_prompt = list()

    instructions = ['# '+l for l in program.instruction]
    lm_prompt = "\n".join([
        *injected_prompt,
        *current_code,
        *instructions,
    ])
    return lm_prompt



def get_code_output(
        python_code: str,
        python_shell: str,
        ) -> str:
    """Return the stdout of executing `python_code` with the Python interpreter.
    `python_shell` is the command used to spawn a Python shell."""
    # Create a temporary Python source file
    with tempfile.NamedTemporaryFile("wt", prefix="natural-python", suffix='.py', delete=False) as python_src_file:
        python_src_file.write(python_code)
        python_src_file.close()
        args = [
            *shlex.split(python_shell),
            python_src_file.name,
        ]
        process = subprocess.run(args, check=False, capture_output=True, text=True)
        if process.returncode != 0:
            raise PythonInterpreterError()
        stdout = process.stdout
    return stdout


def get_new_code_output(
        new_code: list[str],
        current_code: list[str],
        python_shell: str,
        ) -> str:
    """Execute the given prefix (current_code), then execute given suffix
    (new_code) in a Python interpreter. Return the output.
    `python_shell` is the command used to spawn a Python shell."""
    current_code_python = "\n".join(current_code)
    new_code_python = "\n".join([*current_code, *new_code])

    # Execute both copies
    current_stdout = get_code_output(current_code_python, python_shell)
    new_stdout = get_code_output(new_code_python, python_shell)

    # Get code diff
    new_diff = new_stdout[len(current_stdout):]
    return new_diff


def execute_natural_program(
        program: NaturalProgram,
        current_python_code: list[str],
        completion_n: int,
        python_shell: str,
        engine_id: str,
        api_key: str,
        api_base: str,
        max_prediction_tokens: int,
        prediction_temperature: float,
        ) -> tuple[list[str], str]:
    """Returns the new Python code that was executed, and the output of that code to stdout."""
    # Construct prompt
    lm_prompt = get_prompt(current_code=current_python_code, program=program)

    # Sample language model for completions
    completions = get_completions(
        prompt=lm_prompt,
        completion_n=completion_n,
        api_key=api_key,
        api_base=api_base,
        engine_id=engine_id,
        max_tokens=max_prediction_tokens,
        temperature=prediction_temperature,
    )

    # Find a completion that does not crash the program
    for completion in completions:
        new_code = [
            *completion,
            *program.constraint,
        ]
        try:
            output = get_new_code_output(
                new_code=new_code,
                current_code=current_python_code,
                python_shell=python_shell,
            )
            return new_code, output
        except PythonInterpreterError:
            pass

    raise NaturalInterpreterError()
