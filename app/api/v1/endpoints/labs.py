from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.core.config import settings
from app.models.user import User
from app.schemas.lab import (
    Lab,
    LabCreate,
    LabUpdate,
    VM,
    VMUpdate,
    LabAccess
)

router = APIRouter()

@router.post("/labs/", response_model=Lab)
async def create_lab(
    *,
    db: Session = Depends(deps.get_db),
    lab_in: LabCreate,
    current_user: User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks
):
    """
    Create a new lab environment for a challenge.
    """
    # Check if user has any active labs for this challenge
    existing_labs = crud.lab.get_challenge_labs(
        db,
        challenge_id=lab_in.challenge_id,
        active_only=True
    )
    if existing_labs:
        raise HTTPException(
            status_code=400,
            detail="You already have an active lab for this challenge"
        )
    
    lab = crud.lab.create_lab(db, lab_in, current_user.id)
    # Add background task to provision the lab
    background_tasks.add_task(provision_lab, lab.id)
    return lab

@router.get("/labs/", response_model=List[Lab])
def list_user_labs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    include_expired: bool = False,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    List all labs for the current user.
    """
    labs = crud.lab.get_user_labs(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        include_expired=include_expired
    )
    return labs

@router.get("/labs/{lab_id}", response_model=Lab)
def get_lab(
    lab_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get details of a specific lab.
    """
    lab = crud.lab.get_lab(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    if lab.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return lab

@router.put("/labs/{lab_id}", response_model=Lab)
def update_lab(
    *,
    db: Session = Depends(deps.get_db),
    lab_id: int,
    lab_in: LabUpdate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Update a lab (superuser only).
    """
    lab = crud.lab.update_lab(db, lab_id, lab_in)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab

@router.delete("/labs/{lab_id}")
def delete_lab(
    *,
    db: Session = Depends(deps.get_db),
    lab_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks
):
    """
    Delete a lab and its resources.
    """
    lab = crud.lab.get_lab(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    if lab.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Add background task to cleanup resources
    background_tasks.add_task(cleanup_lab_resources, lab_id)
    success = crud.lab.delete_lab(db, lab_id)
    if not success:
        raise HTTPException(status_code=500, detail="Error deleting lab")
    return {"message": "Lab deleted successfully"}

@router.post("/labs/{lab_id}/extend", response_model=Lab)
def extend_lab_time(
    *,
    db: Session = Depends(deps.get_db),
    lab_id: int,
    hours: int = 1,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Extend the expiration time of a lab.
    """
    lab = crud.lab.get_lab(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    if lab.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    extended_lab = crud.lab.extend_lab_time(db, lab_id, hours)
    if not extended_lab:
        raise HTTPException(
            status_code=400,
            detail="Could not extend lab time. Lab may be expired or terminated."
        )
    return extended_lab

@router.get("/labs/{lab_id}/access", response_model=LabAccess)
def get_lab_access(
    lab_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get access information for a lab (VPN config, SSH/RDP commands).
    """
    lab = crud.lab.get_lab(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    if lab.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if not lab.vpn_config:
        raise HTTPException(
            status_code=400,
            detail="Lab is not ready. VPN configuration not available."
        )
    
    ssh_commands = {}
    rdp_commands = {}
    custom_access = {}
    
    for vm in lab.vms:
        if vm.ssh_port:
            ssh_commands[vm.name] = f"ssh -p {vm.ssh_port} user@{settings.LAB_VPN_HOST}"
        if vm.rdp_port:
            rdp_commands[vm.name] = f"{settings.LAB_VPN_HOST}:{vm.rdp_port}"
        if vm.custom_ports:
            custom_access[vm.name] = {
                "host": settings.LAB_VPN_HOST,
                "ports": vm.custom_ports
            }
    
    return LabAccess(
        vpn_config=lab.vpn_config,
        ssh_commands=ssh_commands,
        rdp_commands=rdp_commands,
        custom_access=custom_access
    )

@router.put("/labs/{lab_id}/vms/{vm_id}", response_model=VM)
def update_vm(
    *,
    db: Session = Depends(deps.get_db),
    lab_id: int,
    vm_id: int,
    vm_in: VMUpdate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Update a VM in a lab (superuser only).
    """
    lab = crud.lab.get_lab(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    
    vm = crud.lab.update_vm(db, vm_id, vm_in)
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
    if vm.lab_id != lab_id:
        raise HTTPException(status_code=400, detail="VM does not belong to this lab")
    return vm

# Background tasks (to be implemented in a separate service)
async def provision_lab(lab_id: int):
    """
    Background task to provision a lab environment.
    This should be implemented in a separate service that handles:
    1. Docker container creation
    2. Network setup
    3. VPN configuration
    4. Port forwarding
    5. Resource monitoring
    """
    pass

async def cleanup_lab_resources(lab_id: int):
    """
    Background task to cleanup lab resources.
    This should be implemented in a separate service that handles:
    1. Container cleanup
    2. Network cleanup
    3. VPN configuration removal
    4. Port forwarding cleanup
    """
    pass
