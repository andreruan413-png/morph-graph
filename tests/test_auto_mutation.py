from engine.auto_mutation import AutomaticASTMutator


code = """
def calcular(a, b):
    return a + b
"""


mutator = AutomaticASTMutator()

candidates = mutator.generate(code)


print("================================")
print(" MORPH-GRAPH AUTO MUTATION")
print("================================")

print("\nCÓDIGO ORIGINAL:")
print(code)

print("\nMUTAÇÕES DESCOBERTAS:")

for index, candidate in enumerate(
    candidates,
    start=1
):

    print(
        f"\n--- CANDIDATO {index}: "
        f"{candidate.name} ---"
    )

    print(
        candidate.code()
    )

print(
    f"\nTOTAL: {len(candidates)} candidatos"
)
