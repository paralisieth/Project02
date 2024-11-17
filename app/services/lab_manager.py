import asyncio
import docker
from typing import Dict, List, Optional
import logging
from datetime import datetime
import json

from app.core.config import settings
from app.models.lab import Lab, VirtualMachine, LabStatus
from app.crud.lab import update_lab, update_vm, get_lab
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)
docker_client = docker.from_env()

class LabManager:
    def __init__(self):
        self.network_name = settings.LAB_NETWORK_NAME
        self.vpn_subnet = settings.LAB_VPN_SUBNET
        self.max_labs_per_user = settings.MAX_LABS_PER_USER
        self.max_vms_per_lab = settings.MAX_VMS_PER_LAB
        self._ensure_network()

    def _ensure_network(self):
        """Ensure the Docker network exists."""
        try:
            networks = docker_client.networks.list(names=[self.network_name])
            if not networks:
                docker_client.networks.create(
                    self.network_name,
                    driver="bridge",
                    ipam=docker.types.IPAMConfig(
                        pool_configs=[
                            docker.types.IPAMPool(
                                subnet=self.vpn_subnet
                            )
                        ]
                    )
                )
                logger.info(f"Created network {self.network_name}")
        except Exception as e:
            logger.error(f"Error ensuring network: {e}")
            raise

    async def provision_lab(self, lab_id: int):
        """
        Provision a lab environment including VMs and networking.
        """
        try:
            db = SessionLocal()
            lab = get_lab(db, lab_id)
            if not lab:
                logger.error(f"Lab {lab_id} not found")
                return

            # Update lab status
            lab = update_lab(db, lab_id, {"status": LabStatus.PROVISIONING})

            # Create VPN server for the lab
            vpn_config = await self._create_vpn_server(lab)
            lab = update_lab(db, lab_id, {
                "vpn_config": vpn_config,
                "internal_ip": self._get_next_ip()
            })

            # Provision VMs
            for vm in lab.vms:
                await self._provision_vm(vm)

            # Final lab status update
            lab = update_lab(db, lab_id, {"status": LabStatus.RUNNING})
            logger.info(f"Lab {lab_id} provisioned successfully")

        except Exception as e:
            logger.error(f"Error provisioning lab {lab_id}: {e}")
            if lab:
                update_lab(db, lab_id, {"status": LabStatus.ERROR})
        finally:
            db.close()

    async def _provision_vm(self, vm: VirtualMachine):
        """
        Provision a single VM in the lab environment.
        """
        try:
            # Update VM status
            vm = update_vm(None, vm.id, {"status": LabStatus.PROVISIONING})

            # Create Docker container
            container = docker_client.containers.run(
                image=self._get_image_for_vm_type(vm.vm_type),
                name=f"lab-{vm.lab_id}-{vm.name}",
                detach=True,
                network=self.network_name,
                ports={
                    '22/tcp': vm.ssh_port,
                    '3389/tcp': vm.rdp_port
                } if vm.rdp_port else {'22/tcp': vm.ssh_port},
                environment=self._get_vm_environment(vm),
                volumes=self._get_vm_volumes(vm),
                cpu_count=self._get_vm_cpu_limit(vm.vm_type),
                mem_limit=self._get_vm_memory_limit(vm.vm_type)
            )

            # Update VM with container info
            vm = update_vm(None, vm.id, {
                "status": LabStatus.RUNNING,
                "internal_ip": container.attrs['NetworkSettings']['Networks'][self.network_name]['IPAddress'],
                "docker_container_id": container.id
            })

            logger.info(f"VM {vm.id} provisioned successfully")
            return vm

        except Exception as e:
            logger.error(f"Error provisioning VM {vm.id}: {e}")
            update_vm(None, vm.id, {"status": LabStatus.ERROR})
            raise

    async def cleanup_lab(self, lab_id: int):
        """
        Cleanup lab resources.
        """
        try:
            db = SessionLocal()
            lab = get_lab(db, lab_id)
            if not lab:
                logger.error(f"Lab {lab_id} not found")
                return

            # Update lab status
            lab = update_lab(db, lab_id, {"status": LabStatus.TERMINATING})

            # Cleanup VMs
            for vm in lab.vms:
                await self._cleanup_vm(vm)

            # Cleanup VPN server
            await self._cleanup_vpn_server(lab)

            # Final lab status update
            lab = update_lab(db, lab_id, {"status": LabStatus.TERMINATED})
            logger.info(f"Lab {lab_id} cleaned up successfully")

        except Exception as e:
            logger.error(f"Error cleaning up lab {lab_id}: {e}")
            if lab:
                update_lab(db, lab_id, {"status": LabStatus.ERROR})
        finally:
            db.close()

    async def _cleanup_vm(self, vm: VirtualMachine):
        """
        Cleanup a single VM's resources.
        """
        try:
            if vm.docker_container_id:
                container = docker_client.containers.get(vm.docker_container_id)
                container.stop(timeout=10)
                container.remove()
                logger.info(f"Cleaned up container for VM {vm.id}")

            vm = update_vm(None, vm.id, {"status": LabStatus.TERMINATED})

        except Exception as e:
            logger.error(f"Error cleaning up VM {vm.id}: {e}")
            raise

    def _get_image_for_vm_type(self, vm_type: str) -> str:
        """Get Docker image name for VM type."""
        image_mapping = {
            'UBUNTU': 'ubuntu:20.04',
            'KALI': 'kalilinux/kali-rolling',
            'WINDOWS': 'mcr.microsoft.com/windows:ltsc2019'
        }
        return image_mapping.get(vm_type, 'ubuntu:20.04')

    def _get_vm_environment(self, vm: VirtualMachine) -> Dict[str, str]:
        """Get environment variables for VM."""
        return {
            "VM_NAME": vm.name,
            "LAB_ID": str(vm.lab_id),
            "VM_TYPE": vm.vm_type
        }

    def _get_vm_volumes(self, vm: VirtualMachine) -> Dict[str, Dict[str, str]]:
        """Get volume mappings for VM."""
        return {
            f"/data/labs/{vm.lab_id}/{vm.name}": {
                'bind': '/lab_data',
                'mode': 'rw'
            }
        }

    def _get_vm_cpu_limit(self, vm_type: str) -> int:
        """Get CPU limit based on VM type."""
        cpu_limits = {
            'UBUNTU': 2,
            'KALI': 4,
            'WINDOWS': 4
        }
        return cpu_limits.get(vm_type, 2)

    def _get_vm_memory_limit(self, vm_type: str) -> str:
        """Get memory limit based on VM type."""
        memory_limits = {
            'UBUNTU': '2g',
            'KALI': '4g',
            'WINDOWS': '8g'
        }
        return memory_limits.get(vm_type, '2g')

    def _get_next_ip(self) -> str:
        """Get next available IP in the subnet."""
        # Implement IP allocation logic
        pass

    async def _create_vpn_server(self, lab: Lab) -> str:
        """Create VPN server for lab access."""
        # Implement VPN server creation
        # Return VPN configuration
        pass

    async def _cleanup_vpn_server(self, lab: Lab):
        """Cleanup VPN server."""
        # Implement VPN server cleanup
        pass

# Create singleton instance
lab_manager = LabManager()
