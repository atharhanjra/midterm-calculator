"""
Tests for the calculator REPL (app/calculator_repl.py).

Each test pretends to be a user typing commands, runs the calculator,
and checks what it printed.
"""

import pytest

from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.exceptions import OperationError
from colorama import Fore, Style
from app.operations import OperationFactory


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


def use_temp_folders(monkeypatch, tmp_path):
    """Keep the REPL's history and log files in a temporary test folder."""
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))


@pytest.mark.parametrize("precision, expected", [
    ("2", "0.33"),
    ("4", "0.3333"),
])
def test_repl_precision_setting(monkeypatch, capsys, tmp_path, precision, expected):
    """Changing CALCULATOR_PRECISION changes the result shown in the REPL."""
    use_temp_folders(monkeypatch, tmp_path)
    monkeypatch.setenv("CALCULATOR_PRECISION", precision)
    run_repl(monkeypatch, ["divide", "1", "3", "exit"])
    assert f"Result: {expected}" + Style.RESET_ALL in capsys.readouterr().out


def test_repl_negative_power_in_history(monkeypatch, capsys, tmp_path):
    """2 ** -2 shows 0.25 as the result and in the history."""
    use_temp_folders(monkeypatch, tmp_path)
    run_repl(monkeypatch, ["power", "2", "-2", "history", "exit"])
    output = capsys.readouterr().out
    assert "Result: 0.25" in output
    assert "Power(2, -2) = 0.25" in output


def test_repl_load_respects_history_limit(monkeypatch, capsys, tmp_path):
    """Loading a history file in the REPL keeps only the newest entries."""
    use_temp_folders(monkeypatch, tmp_path)

    # Save 3 calculations to the history file
    calc = Calculator()
    calc.set_operation(OperationFactory.create_operation("add"))
    for number in ["1", "2", "3"]:
        calc.perform_operation(number, number)
    calc.save_history()

    # Allow only 2 entries, then load the file in the REPL
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "2")
    run_repl(monkeypatch, ["load", "history", "exit"])
    output = capsys.readouterr().out
    assert "Addition(2, 2) = 4" in output
    assert "Addition(3, 3) = 6" in output
    assert "Addition(1, 1) = 2" not in output