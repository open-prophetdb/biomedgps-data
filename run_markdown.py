#!/usr/bin/env python3

# Copy from DJRHails's gist
# More details on https://gist.github.com/DJRHails/fa1debd19bd6dbbe9f6789cebdc16b1d

from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional
import contextlib
import re
import subprocess
import sys
import tempfile
import textwrap
import typer

app = typer.Typer()

def get_md_blocks_from_md(file_path: Path) -> list[str]:
    """
    Get all code blocks from a markdown file.

    Args:
        file_path (Path): Path to the markdown file.

    Returns:
        list[str]: A list of all the code blocks in the markdown file.
    """
    # Read the markdown file
    with file_path.open('r') as f:
        md_content = f.read()

    # Use regex to extract code blocks from the parsed markdown
    md_blocks = re.findall(r'(```.*?```)', md_content, re.DOTALL)

    return md_blocks

@dataclass
class CodeBlock:
    language: Optional[str]
    code: str

def execute_python_code(code):
    import ast
    import builtins
    code_ast = ast.parse(code, mode='exec')
    global_scope = {
        '__builtins__': builtins,
    }
    exec(compile(code_ast, '<string>', mode='exec'), global_scope)

# def execute_bash_code(code):
#   with tempfile.TemporaryFile() as f:
#     subprocess.run(code, shell=True, check=True, stdout=f, stderr=f)
#     f.seek(0)
#     sys.stdout.write(f.read().decode())

def execute_bash_code(code):
    # Run the subprocess and capture the output
    result = subprocess.run(code, shell=True, check=True, stdout=subprocess.PIPE, text=True)

    # Print the stdout messages directly to the console
    sys.stdout.write(result.stdout)

@contextlib.contextmanager
def capture_output():
    """
    A context manager to capture stdout/stderr and redirect them to a StringIO object.
    """
    old_stdout, old_stderr = sys.stdout, sys.stderr
    try:
        out = sys.stdout = sys.stderr = StringIO()
        yield out
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr

def execute_code_block(block):
    """
    Execute a code block and display its output in a rich panel.

    Args:
        block (CodeBlock): The code block to execute.
    """
    with capture_output() as output:
        match block.language:
            case "python":
                execute_python_code(block.code)
            case "bash":
                execute_bash_code(block.code)
            case _:
                typer.echo(f"Language {block.language} not supported. Skipping...")

    console = Console()
    console.print(Panel(
        output.getvalue().strip(),
        title="Output",
        border_style="green",
    ))


CODE_BLOCK_RE = r"""(?xm)
^```(?P<language>\w+?)\n
(?P<code>.*?)
^```
"""

def extract_code_block_from_md_block(md_block):
    """
    Extract a code block from a markdown block.

    Args:
        md_block (str): The markdown block to extract the code block from.

    Returns:
        CodeBlock: The extracted code block.
    """
    # Use regex to extract the language from the code block
    matches = re.match(CODE_BLOCK_RE, md_block, re.DOTALL)
    
    # Strip newlines and leading/trailing whitespace from the code
    if matches:
        code = matches.group("code").strip("\n").strip()

        return CodeBlock(
        language=matches.group("language"),
        code=code
        )
    else:
        return CodeBlock(
            language="bash",
            code="printf 'Cannot identify the language. Skipping...\n%s'" % md_block
        )


def snippet_from_block(block):
    """
    Shortens a code block's code to a snippet for display.

    Args:
        block (CodeBlock): The code block to shorten.
    
    Returns:
        str: The shortened code block.
    """
    code = block.code
    if len(code) > 50:
        code = textwrap.shorten(code, width=50, placeholder="...")
    return code

@app.command()
def execute(file_path: Path, run_all: bool = False):
    """
    Execute code blocks from a markdown file.

    Args:
        file_path (Path): Path to the markdown file containing the code blocks.

    """
    console = Console()

    # Get all code blocks from the markdown file
    md_blocks = get_md_blocks_from_md(file_path)

    if not md_blocks:
        console.print(Panel("No code blocks found in the markdown file", title="Error"))
        return

    # Display the code blocks to the user
    code_blocks = [
        extract_code_block_from_md_block(block)
        for block in md_blocks
    ]
    display_blocks = [
        Panel(snippet_from_block(block), title=f"({i}) - {block.language}")
        for i, block in enumerate(code_blocks)
    ]

    grid = Table.grid(expand=True)
    for i in range(0, len(display_blocks), 2):
        grid.add_row(*display_blocks[i:i+2])

    console.print(grid)

    # If the user wants to run all code blocks, execute them and return
    if run_all:
        for block in code_blocks:
            execute_code_block(block)
        return
    else:
        selection = 0
        if len(md_blocks) > 1:
            # Offer the user to select a code block to execute
            selection = typer.prompt("Choose a code block to execute", type=int)

            # Execute the selected code block using the appropriate function
            execute_code_block(code_blocks[selection])
  
if __name__ == "__main__":
    app() 
