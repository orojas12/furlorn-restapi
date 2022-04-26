class TestException(Exception):
    def __init__(self):
        super().__init__("This exception was raised for testing purposes.")
