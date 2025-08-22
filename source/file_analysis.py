def add_numbers(a: float, b: float) -> float:
    """Add two numbers and return the result."""
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers and return the result."""
    return a * b

def greet(name: str) -> str:
    """Return a greeting message for the given name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Example usage when running the script directly
    print(add_numbers(5, 3))
    print(multiply_numbers(4, 2))
    print(greet("Alice"))