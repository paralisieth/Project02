from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.lab import Lab, VirtualMachine, LabStatus
from app.schemas.lab import LabCreate, LabUpdate, VMCreate, VMUpdate
from app.core.config import settings

def create_lab(db: Session, lab: LabCreate, user_id: int) -> Lab:
    # Create the lab
    db_lab = Lab(
        **lab.dict(exclude={'vm_configurations'}),
        user_id=user_id,
        status=LabStatus.CREATING
    )
    db.add(db_lab)
    db.commit()
    db.refresh(db_lab)

    # Create associated VMs
    for vm_config in lab.vm_configurations:
        db_vm = VirtualMachine(
            **vm_config.dict(),
            lab_id=db_lab.id,
            status=LabStatus.CREATING
        )
        db.add(db_vm)
    
    db.commit()
    db.refresh(db_lab)
    return db_lab

def get_lab(db: Session, lab_id: int) -> Optional[Lab]:
    return db.query(Lab).filter(Lab.id == lab_id).first()

def get_user_labs(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    include_expired: bool = False
) -> List[Lab]:
    query = db.query(Lab).filter(Lab.user_id == user_id)
    
    if not include_expired:
        query = query.filter(Lab.expires_at > datetime.utcnow())
    
    return query.offset(skip).limit(limit).all()

def get_challenge_labs(
    db: Session,
    challenge_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
) -> List[Lab]:
    query = db.query(Lab).filter(Lab.challenge_id == challenge_id)
    
    if active_only:
        query = query.filter(
            and_(
                Lab.expires_at > datetime.utcnow(),
                Lab.status == LabStatus.RUNNING
            )
        )
    
    return query.offset(skip).limit(limit).all()

def update_lab(
    db: Session,
    lab_id: int,
    lab_update: LabUpdate
) -> Optional[Lab]:
    db_lab = get_lab(db, lab_id)
    if not db_lab:
        return None
    
    update_data = lab_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_lab, field, value)
    
    db.commit()
    db.refresh(db_lab)
    return db_lab

def delete_lab(db: Session, lab_id: int) -> bool:
    db_lab = get_lab(db, lab_id)
    if not db_lab:
        return False
    
    # Delete associated VMs first
    db.query(VirtualMachine).filter(VirtualMachine.lab_id == lab_id).delete()
    db.delete(db_lab)
    db.commit()
    return True

def get_vm(db: Session, vm_id: int) -> Optional[VirtualMachine]:
    return db.query(VirtualMachine).filter(VirtualMachine.id == vm_id).first()

def update_vm(
    db: Session,
    vm_id: int,
    vm_update: VMUpdate
) -> Optional[VirtualMachine]:
    db_vm = get_vm(db, vm_id)
    if not db_vm:
        return None
    
    update_data = vm_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vm, field, value)
    
    db.commit()
    db.refresh(db_vm)
    return db_vm

def cleanup_expired_labs(db: Session) -> int:
    """
    Cleanup expired labs and their associated resources.
    Returns the number of labs cleaned up.
    """
    expired_labs = db.query(Lab).filter(
        and_(
            Lab.expires_at <= datetime.utcnow(),
            Lab.status != LabStatus.TERMINATED
        )
    ).all()
    
    count = 0
    for lab in expired_labs:
        lab.status = LabStatus.TERMINATED
        for vm in lab.vms:
            vm.status = LabStatus.TERMINATED
        count += 1
    
    db.commit()
    return count

def extend_lab_time(
    db: Session,
    lab_id: int,
    hours: int = 1
) -> Optional[Lab]:
    """
    Extend the expiration time of a lab.
    """
    db_lab = get_lab(db, lab_id)
    if not db_lab or db_lab.status == LabStatus.TERMINATED:
        return None
    
    # Don't extend if already expired
    if db_lab.expires_at <= datetime.utcnow():
        return None
    
    db_lab.expires_at += timedelta(hours=hours)
    db.commit()
    db.refresh(db_lab)
    return db_lab

def get_lab_status(db: Session, lab_id: int) -> Dict:
    """
    Get detailed status information about a lab and its VMs.
    """
    db_lab = get_lab(db, lab_id)
    if not db_lab:
        return None
    
    return {
        "lab_status": db_lab.status,
        "expires_at": db_lab.expires_at,
        "time_remaining": (db_lab.expires_at - datetime.utcnow()).total_seconds(),
        "vms": [
            {
                "name": vm.name,
                "status": vm.status,
                "type": vm.vm_type,
                "internal_ip": vm.internal_ip,
                "ssh_port": vm.ssh_port,
                "rdp_port": vm.rdp_port
            }
            for vm in db_lab.vms
        ]
    }
