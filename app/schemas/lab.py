from typing import Optional, List, Dict, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import json

from app.models.lab import LabStatus, VMType

class VMBase(BaseModel):
    name: str
    vm_type: VMType
    ssh_port: Optional[int] = None
    rdp_port: Optional[int] = None
    custom_ports: Optional[str] = None

    @validator('custom_ports')
    def validate_custom_ports(cls, v):
        if v:
            try:
                ports = json.loads(v)
                if not isinstance(ports, dict):
                    raise ValueError("Custom ports must be a JSON object")
                for port in ports.values():
                    if not isinstance(port, int):
                        raise ValueError("Port numbers must be integers")
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for custom ports")
        return v

class VMCreate(VMBase):
    lab_id: int

class VMUpdate(VMBase):
    status: Optional[LabStatus] = None
    internal_ip: Optional[str] = None
    vm_config: Optional[Dict] = None

class VM(VMBase):
    id: int
    status: LabStatus
    lab_id: int
    internal_ip: Optional[str]
    created_at: datetime
    docker_container_id: Optional[str]
    vm_config: Optional[Dict]

    class Config:
        orm_mode = True

class LabBase(BaseModel):
    name: str
    description: Optional[str] = None
    challenge_id: int

class LabCreate(LabBase):
    expires_at: datetime
    vm_configurations: List[VMCreate]

class LabUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[LabStatus] = None
    vpn_config: Optional[str] = None
    internal_ip: Optional[str] = None
    expires_at: Optional[datetime] = None

class Lab(LabBase):
    id: int
    status: LabStatus
    user_id: int
    vpn_config: Optional[str]
    internal_ip: Optional[str]
    created_at: datetime
    expires_at: datetime
    last_accessed: Optional[datetime]
    vms: List[VM] = []

    class Config:
        orm_mode = True

class LabAccess(BaseModel):
    vpn_config: str
    ssh_commands: Dict[str, str]
    rdp_commands: Dict[str, str]
    custom_access: Dict[str, Dict[str, Union[str, int]]]
