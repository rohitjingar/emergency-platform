class AppException(Exception):
    """Base exception for all application errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class DuplicateEmailError(AppException):
    def __init__(self):
        super().__init__("Email already registered", status_code=400)

class InvalidRoleError(AppException):
    def __init__(self, valid_roles: set):
        super().__init__(
            f"Invalid role. Must be one of: {valid_roles}",
            status_code=400
        )

class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__("Invalid email or password", status_code=401)

class IncidentNotFoundError(AppException):
    def __init__(self, incident_id: int):
        super().__init__(f"Incident {incident_id} not found", status_code=404)

class AIServiceError(AppException):
    def __init__(self, message: str):
        super().__init__(f"AI service error: {message}", status_code=503)
        
class DuplicateIncidentError(AppException):
    def __init__(self):
        super().__init__(
            "Duplicate incident: same location reported within 5 minutes. "
            "Your original report is already being processed.",
            status_code=409  # 409 Conflict — semantically correct for duplicates
        )