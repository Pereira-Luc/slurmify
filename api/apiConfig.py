from typing import List, Optional
from pydantic import BaseModel


class ConfigRequest(BaseModel):
    """Request model for configuration validation"""

    code: str


class ParameterRequest(BaseModel):
    """Request model for parameter validation"""

    name: str
    account: str
    exec_command: list[str] | str
    cores: int = int | None
    gpu: int | None = None
    mode: str = "default"
    nodes: int | None = None
    time: str = "00:15:00"
    ntasks: int = 1
    partition: str = "cpu"
    environment_commands: list[str] | None = None
    module_names: list[str] | None = None
    logs_default: str | None = None
    logs_error: str | None = None

    def __str__(self):
        return f"Current Configuration: {self.name}, {self.account}, {self.exec_command}, {self.cores}, {self.gpu}, {self.mode}, {self.nodes}, {self.time}, {self.ntasks}, {self.partition}, {self.environment_commands}, {self.module_names}, {self.logs_default}, {self.logs_error}"


class ValidationResult(BaseModel):
    """Result for individual job validation"""

    job_name: str
    valid: bool
    result: str
    report: Optional[str] = None


class ValidationResponse(BaseModel):
    """Response model for validation results"""

    valid: bool
    results: List[ValidationResult]
    error: Optional[str] = None
