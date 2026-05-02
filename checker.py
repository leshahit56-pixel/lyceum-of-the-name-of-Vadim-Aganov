from unittest.mock import patch
import pycodestyle
import io
from contextlib import redirect_stdout
import sys


def check_pep8(solution):
    f = io.StringIO(solution)
    checker = pycodestyle.Checker(
        filename='solution.py',
        lines=f.readlines()
    )

    out = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = out
    checker.check_all()
    sys.stdout = old_stdout

    errors = out.getvalue().strip()
    error_lines = [line for line in errors.split('\n') if 'W292' not in line and 'E901' not in line]

    if not error_lines:
        return "ok"
    return " | ".join(error_lines)


def run_single_test(solution, test_input, expected):
    result = {
        "verdict": "",
        "test_input": test_input,
        "expected": expected,
        "output": "",
        "error": ""
    }

    with patch('builtins.input', side_effect=test_input):
        f = io.StringIO()

        with redirect_stdout(f):
            try:
                exec(solution, {}, {})
            except SyntaxError:
                result['output'] = None
                result['verdict'] = 'ошибка компиляции'
                result["error"] = "SyntaxError"
                return result
            except Exception as e:
                result['output'] = None
                result['verdict'] = "ошибка выполнения"
                result["error"] = f"{type(e).__name__}: {e}"
                return result

        answer = f.getvalue().rstrip('\n')
        answer = answer.split('\n')
        result["output"] = answer

        if answer == expected:
            result["verdict"] = "ok"
        else:
            result["verdict"] = "неверный ответ"

        return result


def first_first(solution, tests):
    result = {
        "verdict": "",
        "PEP8": "",
        "test_number": 0,
        "test_input": "",
        "expected": "",
        "output": "",
        "error": ""
    }

    result['PEP8'] = check_pep8(solution)
    if result['PEP8'] != 'ok':
        result['verdict'] = 'код не соответствует стандарту PEP8'
        return result

    # Прогон по всем тестам
    for i, test in enumerate(tests, 1):
        single_result = run_single_test(solution, test["input"], test["expected"])

        if single_result["verdict"] != "ok":
            result["verdict"] = single_result["verdict"]
            result["test_number"] = i
            result["test_input"] = single_result["test_input"]
            result["expected"] = single_result["expected"]
            result["output"] = single_result["output"]
            result["error"] = single_result["error"]
            return result

    result["verdict"] = "ok"
    return result