from typing import Dict, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class ConnectionService:
    def __init__(self):
        self.connections = {}
        logger.info("Initialized Connection Service")

    async def get_connection_info(self, vm_id: str, connection_type: str = "rdp") -> Dict:
        """Get connection information for a VM."""
        try:
            if connection_type.lower() == "rdp":
                return {
                    "protocol": "rdp",
                    "hostname": "192.168.1.100",  # This would be dynamic in production
                    "port": 3389,
                    "username": "ubuntu",  # Default username
                    "password": "training123",  # In production, this would be securely stored
                    "command": 'mstsc.exe /v:192.168.1.100'  # Windows RDP command
                }
            elif connection_type.lower() == "ssh":
                return {
                    "protocol": "ssh",
                    "hostname": "192.168.1.100",
                    "port": 22,
                    "username": "ubuntu",
                    "command": 'ssh ubuntu@192.168.1.100'
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported connection type: {connection_type}"
                )
        except Exception as e:
            logger.error(f"Error getting connection info: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get connection information: {str(e)}"
            )

connection_service = ConnectionService()
