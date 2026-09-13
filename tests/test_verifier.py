from engine.verifier import verify_python_code


good_code = """
def soma(a, b):
    return a + b


assert soma(2, 3) == 5

print("TESTE PASSOU")
"""


bad_code = """
def soma(a, b):
    return a - b


assert soma(2, 3) == 5
"""


print("=== TESTANDO CÓDIGO CORRETO ===")

result = verify_python_code(good_code)

print(result.as_dict())


print("\n=== TESTANDO CÓDIGO INCORRETO ===")

result = verify_python_code(bad_code)

print(result.as_dict())
