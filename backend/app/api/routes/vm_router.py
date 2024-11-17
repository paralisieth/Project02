from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.services.vm_service import vm_service
from app.services.connection_service import connection_service
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[dict])
async def list_vms(current_user: dict = Depends(get_current_user)):
    """List all available virtual machines."""
    return await vm_service.list_vms()

@router.post("/{vm_id}/start")
async def start_vm(vm_id: str, current_user: dict = Depends(get_current_user)):
    """Start a virtual machine."""
    return await vm_service.start_vm(vm_id)

@router.post("/{vm_id}/stop")
async def stop_vm(vm_id: str, current_user: dict = Depends(get_current_user)):
    """Stop a virtual machine."""
    return await vm_service.stop_vm(vm_id)

@router.get("/{vm_id}")
async def get_vm_info(vm_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed information about a virtual machine."""
    return await vm_service.get_vm_info(vm_id)

@router.get("/{vm_id}/rdp")
async def get_vm_rdp_info(vm_id: str, current_user: dict = Depends(get_current_user)):
    """Get RDP connection information for a virtual machine."""
    return await vm_service.get_vm_rdp_info(vm_id)

@router.get("/{vm_id}/connect")
async def get_connection_info(
    vm_id: str, 
    connection_type: str = "rdp",
    current_user: dict = Depends(get_current_user)
):
    """Get connection information for a virtual machine."""
    # First check if VM exists and is running
    vm = await vm_service.get_vm_info(vm_id)
    if vm["state"] != "running":
        raise HTTPException(
            status_code=400,
            detail="VM must be running to get connection information"
        )
    return await connection_service.get_connection_info(vm_id, connection_type)
