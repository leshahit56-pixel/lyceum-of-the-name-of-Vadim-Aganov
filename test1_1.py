from unittest.mock import patch
import io
from contextlib import redirect_stdout

def first_first(solution):

    result = {
        "verdict": "",
        "output": "",
        "error": "",
        "PEP8": "",
    }

    
            
    f = io.StringIO()

    with redirect_stdout(f):
        try:
            exec(solution, {}, {})
        except SyntaxError:
            result['verdict'] = 'ошибка кампиляции'
            result["error"] = 'SyntaxError'

        except Exception as e:
            result['verdict'] = 'ошибка в выполнении кода'
            result["error"] = f'{type(e).__name__}: {e}'
    answer = f.getvalue().strip()

    

    return answer
code = '''print('Hello world!')'''
print(first_first(code))




