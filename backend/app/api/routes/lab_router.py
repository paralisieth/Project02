from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.core.auth import get_current_user
import uuid
from datetime import datetime

router = APIRouter()

# Mock lab data
MOCK_LABS = {
    "lab-1": {
        "id": "lab-1",
        "name": "Web Application Security Lab",
        "description": "Learn about common web vulnerabilities and how to exploit them",
        "difficulty": "Intermediate",
        "vms": ["vm-1"],
        "status": "running",
        "created_at": datetime.now().isoformat()
    },
    "lab-2": {
        "id": "lab-2",
        "name": "Network Penetration Testing Lab",
        "description": "Practice network scanning, enumeration, and exploitation",
        "difficulty": "Advanced",
        "vms": ["vm-1", "vm-2"],
        "status": "stopped",
        "created_at": datetime.now().isoformat()
    }
}

@router.get("/")
async def list_labs(current_user: dict = Depends(get_current_user)):
    """List all available labs."""
    return list(MOCK_LABS.values())

@router.get("/{lab_id}")
async def get_lab(lab_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed information about a lab."""
    if lab_id not in MOCK_LABS:
        raise HTTPException(status_code=404, detail="Lab not found")
    return MOCK_LABS[lab_id]

@router.post("/")
async def create_lab(
    name: str,
    description: str,
    difficulty: str,
    vm_ids: List[str],
    current_user: dict = Depends(get_current_user)
):
    """Create a new lab environment."""
    lab_id = str(uuid.uuid4())
    new_lab = {
        "id": lab_id,
        "name": name,
        "description": description,
        "difficulty": difficulty,
        "vms": vm_ids,
        "status": "stopped",
        "created_at": datetime.now().isoformat()
    }
    MOCK_LABS[lab_id] = new_lab
    return new_lab

@router.post("/{lab_id}/start")
async def start_lab(lab_id: str, current_user: dict = Depends(get_current_user)):
    """Start a lab environment."""
    if lab_id not in MOCK_LABS:
        raise HTTPException(status_code=404, detail="Lab not found")
    
    lab = MOCK_LABS[lab_id]
    if lab["status"] == "running":
        return lab
    
    lab["status"] = "running"
    return lab

@router.post("/{lab_id}/stop")
async def stop_lab(lab_id: str, current_user: dict = Depends(get_current_user)):
    """Stop a lab environment."""
    if lab_id not in MOCK_LABS:
        raise HTTPException(status_code=404, detail="Lab not found")
    
    lab = MOCK_LABS[lab_id]
    if lab["status"] == "stopped":
        return lab
    
    lab["status"] = "stopped"
    return lab

@router.delete("/{lab_id}")
async def delete_lab(lab_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a lab environment."""
    if lab_id not in MOCK_LABS:
        raise HTTPException(status_code=404, detail="Lab not found")
    
    lab = MOCK_LABS.pop(lab_id)
    return {"message": f"Lab {lab['name']} deleted successfully"}
