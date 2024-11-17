from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base

class LabStatus(str, enum.Enum):
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    TERMINATED = "terminated"

class VMType(str, enum.Enum):
    UBUNTU = "ubuntu"
    KALI = "kali"
    WINDOWS = "windows"
    CUSTOM = "custom"

class Lab(Base):
    __tablename__ = "labs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(Enum(LabStatus), default=LabStatus.CREATING)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    vpn_config = Column(Text)  # OpenVPN configuration for lab access
    internal_ip = Column(String(15))  # Internal IP address in the lab network
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_accessed = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="labs")
    challenge = relationship("Challenge", back_populates="labs")
    vms = relationship("VirtualMachine", back_populates="lab")

class VirtualMachine(Base):
    __tablename__ = "virtual_machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    vm_type = Column(Enum(VMType), nullable=False)
    status = Column(Enum(LabStatus), default=LabStatus.CREATING)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
    internal_ip = Column(String(15))  # Internal IP in the lab network
    ssh_port = Column(Integer)  # SSH port for access
    rdp_port = Column(Integer)  # RDP port for Windows VMs
    custom_ports = Column(String(255))  # JSON string of additional port mappings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    docker_container_id = Column(String(64))  # Docker container ID if using containers
    vm_config = Column(Text)  # JSON configuration for the VM

    # Relationships
    lab = relationship("Lab", back_populates="vms")
