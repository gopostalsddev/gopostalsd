class Result:
    def __init__(self, status: bool = True, data=None, error: str = None, details: str = None):
        self.status = status
        self.data = data
        self.error = error
        self.details = details
