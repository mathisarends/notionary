import re

# Current regex
COLUMNS_START = re.compile(r"^:::\s*columns\s*$")

# Test strings
test_strings = [
    "::: columns",
    ":::columns", 
    "::: columns ",
    " ::: columns",
    ":::  columns  "
]

print("Testing current regex:")
for test in test_strings:
    result = bool(COLUMNS_START.match(test.strip()))
    print(f"'{test}' -> {result}")

# Fixed regex - more flexible
COLUMNS_START_FIXED = re.compile(r"^:::\s*columns\s*$", re.IGNORECASE)

print("\nTesting fixed regex:")
for test in test_strings:
    result = bool(COLUMNS_START_FIXED.match(test.strip()))
    print(f"'{test}' -> {result}")

# Test the exact string from your log
exact_string = "::: columns"
print(f"\nExact test: '{exact_string}' -> {bool(COLUMNS_START.match(exact_string.strip()))}")