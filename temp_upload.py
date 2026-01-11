class DataProcessor:
    """Existing docstring."""
    backend_type = "SQL"
    
    def process(self, data: list, mode: str = "fast") -> int:
        if not data:
            raise ValueError("Data cannot be empty")
        return len(data)

    def data_generator(self):
        yield 1
        yield 2
