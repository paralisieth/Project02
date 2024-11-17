from typing import List, Optional
from fastapi import HTTPException
import asyncio
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Mock VM data
MOCK_VMS = {
    "vm-1": {
        "id": "vm-1",
        "name": "Ubuntu-Lab-1",
        "state": "running",
        "memory": 4096,
        "cpu_count": 2,
        "os": "Ubuntu 20.04",
        "ip_address": "192.168.1.100",
        "created_at": datetime.now().isoformat()
    },
    "vm-2": {
        "id": "vm-2",
        "name": "Kali-Lab",
        "state": "stopped",
        "memory": 8192,
        "cpu_count": 4,
        "os": "Kali Linux",
        "ip_address": "192.168.1.101",
        "created_at": datetime.now().isoformat()
    }
}

class VMService:
    def __init__(self):
        self.vms = MOCK_VMS.copy()
        logger.info("Initialized Mock VM Service")

    async def list_vms(self) -> List[dict]:
        """List all available virtual machines."""
        try:
            return list(self.vms.values())
        except Exception as e:
            logger.error(f"Error listing VMs: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to list virtual machines")

    async def start_vm(self, vm_id: str) -> dict:
        """Start a virtual machine."""
        try:
            if vm_id not in self.vms:
                raise HTTPException(status_code=404, detail="VM not found")
            
            vm = self.vms[vm_id]
            if vm["state"] == "running":
                return vm
            
            vm["state"] = "running"
            return vm
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error starting VM {vm_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to start VM: {str(e)}")

    async def stop_vm(self, vm_id: str) -> dict:
        """Stop a virtual machine."""
        try:
            if vm_id not in self.vms:
                raise HTTPException(status_code=404, detail="VM not found")
            
            vm = self.vms[vm_id]
            if vm["state"] == "stopped":
                return vm
            
            vm["state"] = "stopped"
            return vm
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error stopping VM {vm_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to stop VM: {str(e)}")

    async def get_vm_info(self, vm_id: str) -> dict:
        """Get detailed information about a virtual machine."""
        try:
            if vm_id not in self.vms:
                raise HTTPException(status_code=404, detail="VM not found")
            
            return self.vms[vm_id]
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting VM info for {vm_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get VM info: {str(e)}")

    async def create_vm(self, name: str, memory: int, cpu_count: int, os: str) -> dict:
        """Create a new virtual machine."""
        try:
            vm_id = str(uuid.uuid4())
            new_vm = {
                "id": vm_id,
                "name": name,
                "state": "stopped",
                "memory": memory,
                "cpu_count": cpu_count,
                "os": os,
                "ip_address": f"192.168.1.{len(self.vms) + 100}",
                "created_at": datetime.now().isoformat()
            }
            self.vms[vm_id] = new_vm
            return new_vm
        except Exception as e:
            logger.error(f"Error creating VM: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create VM: {str(e)}")

    async def delete_vm(self, vm_id: str) -> dict:
        """Delete a virtual machine."""
        try:
            if vm_id not in self.vms:
                raise HTTPException(status_code=404, detail="VM not found")
            
            vm = self.vms.pop(vm_id)
            return {"message": f"VM {vm['name']} deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting VM {vm_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete VM: {str(e)}")

vm_service = VMService()
