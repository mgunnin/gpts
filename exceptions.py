class MissingEnvironmentVariableError(Exception):
    """Exception raised when a required environment variable is missing."""

    def __init__(self, environment_variable):
        self.environment_variable = environment_variable
        self.message = f"{self.environment_variable} environment variable is not set"
        super().__init__(self.message)
