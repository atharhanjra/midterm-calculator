# Enhanced Calculator (Midterm Project)

A command-line calculator built in Python. You type a command, enter two numbers, and it shows the result. It keeps a history of calculations, supports undo and redo, saves history to a CSV file with pandas, and logs every calculation to a log file.

## Features

- **10 operations:** add, subtract, multiply, divide, power, root, modulus, integer division, percentage, and absolute difference
- **History:** view, clear, save, and load calculation history (stored as CSV using pandas)
- **Undo / redo:** go back or forward one calculation at a time
- **Logging:** every calculation and error is written to a log file
- **Configuration:** settings are loaded from a `.env` file
- **Color-coded output:** results in green, errors in red, warnings in yellow
- **Error handling:** clear messages for invalid input, unknown commands, and dividing by zero

## Design Patterns

- **Factory:** `OperationFactory` creates the right operation from what the user types
- **Strategy:** each operation is its own class with an `execute()` method
- **Observer:** `LoggingObserver` logs each calculation, and `AutoSaveObserver` saves history after each calculation
- **Memento:** `CalculatorMemento` saves snapshots of history for undo and redo
- **Facade:** the `Calculator` class gives one simple interface to everything else

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/atharhanjra/midterm-calculator.git
   cd midterm-calculator
   ```
2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration (.env file)

Settings are stored in a `.env` file in the main project folder and loaded with `python-dotenv`. If a setting is missing, the calculator uses its default value.

| Setting | What it does | Default |
|---|---|---|
| `CALCULATOR_LOG_DIR` | Folder for log files | `logs/` |
| `CALCULATOR_LOG_FILE` | Log file path | `logs/calculator.log` |
| `CALCULATOR_HISTORY_DIR` | Folder for history files | `history/` |
| `CALCULATOR_HISTORY_FILE` | History CSV file path | `history/calculator_history.csv` |
| `CALCULATOR_MAX_HISTORY_SIZE` | Most calculations kept in history | `1000` |
| `CALCULATOR_AUTO_SAVE` | Save history after every calculation (`true` or `false`) | `true` |
| `CALCULATOR_PRECISION` | Number of decimal places | `10` |
| `CALCULATOR_MAX_INPUT_VALUE` | Largest number allowed | `1e999` |
| `CALCULATOR_DEFAULT_ENCODING` | Encoding for files | `utf-8` |

Example `.env`:

```
CALCULATOR_MAX_HISTORY_SIZE=1000
CALCULATOR_AUTO_SAVE=true
CALCULATOR_PRECISION=10
CALCULATOR_MAX_INPUT_VALUE=1e999
CALCULATOR_DEFAULT_ENCODING=utf-8
```

### Logging

All logging goes through the `Logger` class in `app/logger.py`, which uses Python's `logging` module. Calculations are logged at the INFO level, and errors at the ERROR level. To change where logs are saved, set `CALCULATOR_LOG_DIR` or `CALCULATOR_LOG_FILE` in the `.env` file.

## Usage

Start the calculator:

```
python3 main.py
```

Type a command. For calculations, enter the two numbers when asked:

```
Enter command: percent

Enter numbers (or 'cancel' to abort):
First number: 50
Second number: 200

Result: 25
```

### Commands

| Command | What it does |
|---|---|
| `add` | Adds two numbers |
| `subtract` | Subtracts the second number from the first |
| `multiply` | Multiplies two numbers |
| `divide` | Divides the first number by the second |
| `power` | Raises the first number to the power of the second |
| `root` | Takes the nth root (second number is n) |
| `modulus` | Remainder after dividing the first number by the second |
| `int_divide` | Divides and drops the decimal part |
| `percent` | What percent the first number is of the second: (a / b) * 100 |
| `abs_diff` | The positive difference between two numbers |
| `history` | Shows past calculations |
| `clear` | Clears the history |
| `undo` | Undoes the last calculation |
| `redo` | Redoes the last undone calculation |
| `save` | Saves the history to the CSV file |
| `load` | Loads the history from the CSV file |
| `help` | Shows the list of commands |
| `exit` | Saves history and exits |

Type `cancel` at either number prompt to stop a calculation.

## Running Tests

```
pytest --cov=app --cov-report=term-missing
```

This runs all the tests and shows the coverage for each file, including any lines that aren't tested.

## CI/CD with GitHub Actions

The workflow in `.github/workflows/python-app.yml` runs automatically on every push and pull request to `main`. It:

1. checks out the code
2. sets up Python 3.12
3. installs the dependencies from `requirements.txt`
4. runs the tests with coverage, and fails if coverage is below 90%