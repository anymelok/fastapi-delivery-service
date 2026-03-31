class ExternalServiceException(Exception):
    def __init__(self, message, service_name, status_code) -> None:
        self.message = message
        self.service_name = service_name
        self.status_code = status_code
        super().__init__(self.message)
