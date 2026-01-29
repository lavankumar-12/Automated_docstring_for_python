"""Sample module for testing docstring generation."""

def add(a, b):
    """This is add function."""
    return a + b

def greet(name: str, age=20) -> str:    
    """This is the greeting function."""
    return f"Hello {name}"

class Calculator:
    """A simple calculator class."""
    def multiply(self, x, y):
        """Multiplies two numbers."""
        return x * y
    def divide(self, x, y):
        """Divides two numbers."""
        return x / y
    def subtract(self, x, y):
        """Subtracts two numbers."""
        return x - y
    