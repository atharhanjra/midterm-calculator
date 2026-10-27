"""
Tests for the calculator REPL (app/calculator_repl.py).

Each test pretends to be a user typing commands, runs the calculator,
and checks what it printed.
"""

import pytest

from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.exceptions import OperationError
from colorama import Fore


def run_repl(monkeypatch, inputs):
    """Pretend the user typed each item in inputs, then run the calculator."""
    answers = iter(inputs)

    def fake_input(prompt):
        answer = next(answers)
        # Special words that simulate pressing Ctrl+C or Ctrl+D
        if answer == "CTRL_C":
            raise KeyboardInterrupt
        if answer == "CTRL_D":
            raise EOFError
        return answer

    monkeypatch.setattr("builtins.input", fake_input)
    calculator_repl()


def broken(self):
    """Stand-in for save or load that always fails."""
    raise OperationError("disk full")


@pytest.mark.parametrize("inputs, expected", [
    (["help", "exit"], "Available commands"),
    (["exit"], "Goodbye!"),
    (["clear", "exit"], "History cleared"),
    (["clear", "history", "exit"], "No calculations in history"),
    (["undo", "exit"], "Nothing to undo"),
    (["redo", "exit"], "Nothing to redo"),
    (["save", "exit"], "History saved successfully"),
    (["load", "exit"], "History loaded successfully"),
    (["hello", "exit"], "Unknown command: 'hello'"),
])
def test_commands(monkeypatch, capsys, inputs, expected):
    """Each command prints the right message."""
    run_repl(monkeypatch, inputs)
    assert expected in capsys.readouterr().out


def test_calculation_and_history(monkeypatch, capsys):
    """A calculation prints its result and shows up in history."""
    run_repl(monkeypatch, ["add", "2", "3", "history", "exit"])
    output = capsys.readouterr().out
    assert "Result: 5" in output
    assert "Calculation History" in output


def test_undo_and_redo(monkeypatch, capsys):
    """Undo removes the last calculation and redo brings it back."""
    run_repl(monkeypatch, ["add", "2", "3", "undo", "redo", "exit"])
    output = capsys.readouterr().out
    assert "Operation undone" in output
    assert "Operation redone" in output


@pytest.mark.parametrize("inputs", [
    ["add", "cancel", "exit"],
    ["add", "2", "cancel", "exit"],
])
def test_cancel(monkeypatch, capsys, inputs):
    """Typing cancel at either number stops the calculation."""
    run_repl(monkeypatch, inputs)
    assert "Operation cancelled" in capsys.readouterr().out


def test_invalid_number(monkeypatch, capsys):
    """A non-number shows an error instead of crashing."""
    run_repl(monkeypatch, ["add", "abc", "3", "exit"])
    assert "Error:" in capsys.readouterr().out


@pytest.mark.parametrize("command, method, expected", [
    ("save", "save_history", "Error saving history: disk full"),
    ("load", "load_history", "Error loading history: disk full"),
    ("exit", "save_history", "Warning: Could not save history: disk full"),
])
def test_save_and_load_errors(monkeypatch, capsys, command, method, expected):
    """Save, load, and exit show a clear message if saving or loading fails."""
    monkeypatch.setattr(Calculator, method, broken)
    inputs = ["exit"] if command == "exit" else [command, "exit"]
    run_repl(monkeypatch, inputs)
    assert expected in capsys.readouterr().out


def test_ctrl_c(monkeypatch, capsys):
    """Ctrl+C cancels the current input without quitting."""
    run_repl(monkeypatch, ["CTRL_C", "exit"])
    assert "Operation cancelled" in capsys.readouterr().out


def test_ctrl_d(monkeypatch, capsys):
    """Ctrl+D ends the calculator."""
    run_repl(monkeypatch, ["CTRL_D"])
    assert "Input terminated. Exiting..." in capsys.readouterr().out


def test_fatal_error(monkeypatch, capsys):
    """If the calculator can't start, the error is shown and re-raised."""
    def broken_calculator():
        raise RuntimeError("boom")

    monkeypatch.setattr("app.calculator_repl.Calculator", broken_calculator)
    with pytest.raises(RuntimeError):
        calculator_repl()
    assert "Fatal error: boom" in capsys.readouterr().out


@pytest.mark.parametrize("inputs, expected", [
    (["add", "2", "3", "exit"], Fore.GREEN + "\nResult: 5"),
    (["add", "abc", "3", "exit"], Fore.RED + "Error:"),
    (["hello", "exit"], Fore.YELLOW + "Unknown command"),
])
def test_colored_output(monkeypatch, capsys, inputs, expected):
    """Results are green, errors are red, and unknown commands are yellow."""
    run_repl(monkeypatch, inputs)
    assert expected in capsys.readouterr().out