import re

# 简化后的正则表达式
pattern = r"^[a-zA-Z0-9_]+::.+::[a-zA-Z0-9_]+:[a-zA-Z0-9_]+$"
test_values = [
    "bioarx::VirGenHumGen:Gene:Gene",
    "bioarx::HumGenHumGen:Gene:Gene",
    "bioarx::DrugHumGen:Compound:Gene",
    "bioarx::DrugVirGen:Compound:Gene",
]

print("Regex pattern:", pattern)
for value in test_values:
    print("Testing value:", value)
    if re.match(pattern, value):
        print(f"Match: {value}")
    else:
        print(f"No match: {value}")
