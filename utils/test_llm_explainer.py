"""Send a small Python example to local Qwen and print its explanation."""

from llm_explainer import explain_code


SAMPLE_CODE = '''
def calculate_total(prices):
    """Return the sum of all prices."""
    total = 0
    for price in prices:
        total += price
    return total


items = [4.50, 2.25, 3.00]
print(calculate_total(items))
'''


if __name__ == "__main__":
    try:
        print(explain_code(SAMPLE_CODE))
    except (RuntimeError, ValueError) as exc:
        print(f"Explanation failed: {exc}")
        raise SystemExit(1)
