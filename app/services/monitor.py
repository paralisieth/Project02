import asyncio
import psutil
import docker
import logging
from typing import Dict, List
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.lab import Lab, VirtualMachine, LabStatus
from app.crud.lab import get_lab, update_lab, update_vm
from app.db.session import SessionLocal
from app.services.lab_manager import lab_manager

logger = logging.getLogger(__name__)
docker_client = docker.from_env()

class ResourceMonitor:
    def __init__(self):
        self.check_interval = settings.MONITOR_CHECK_INTERVAL
        self.cpu_threshold = settings.MONITOR_CPU_THRESHOLD
        self.memory_threshold = settings.MONITOR_MEMORY_THRESHOLD
        self.disk_threshold = settings.MONITOR_DISK_THRESHOLD
        self.running = False

    async def start(self):
        """Start the monitoring service."""
        self.running = True
        while self.running:
            try:
                await self._check_resources()
                await self._cleanup_expired_labs()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(self.check_interval)

    async def stop(self):
        """Stop the monitoring service."""
        self.running = False

    async def _check_resources(self):
        """Check system and container resources."""
        try:
            # Check system resources
            system_stats = self._get_system_stats()
            if self._is_system_overloaded(system_stats):
                await self._handle_system_overload()

            # Check container resources
            containers = docker_client.containers.list(
                filters={"label": "lab_container=true"}
            )
            for container in containers:
                stats = container.stats(stream=False)
                if self._is_container_overloaded(stats):
                    await self._handle_container_overload(container)

        except Exception as e:
            logger.error(f"Error checking resources: {e}")

    def _get_system_stats(self) -> Dict:
        """Get system resource statistics."""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent
        }

    def _is_system_overloaded(self, stats: Dict) -> bool:
        """Check if system resources are overloaded."""
        return (
            stats["cpu_percent"] > self.cpu_threshold or
            stats["memory_percent"] > self.memory_threshold or
            stats["disk_percent"] > self.disk_threshold
        )

    def _is_container_overloaded(self, stats: Dict) -> bool:
        """Check if container resources are overloaded."""
        cpu_percent = self._calculate_container_cpu_percent(stats)
        memory_percent = self._calculate_container_memory_percent(stats)
        return (
            cpu_percent > self.cpu_threshold or
            memory_percent > self.memory_threshold
        )

    async def _handle_system_overload(self):
        """Handle system resource overload."""
        logger.warning("System resources overloaded")
        try:
            db = SessionLocal()
            # Get all running labs
            running_labs = (
                db.query(Lab)
                .filter(Lab.status == LabStatus.RUNNING)
                .all()
            )

            # Sort labs by creation time and terminate oldest if necessary
            running_labs.sort(key=lambda x: x.created_at)
            if running_labs:
                oldest_lab = running_labs[0]
                logger.info(f"Terminating oldest lab {oldest_lab.id} due to system overload")
                await lab_manager.cleanup_lab(oldest_lab.id)

        except Exception as e:
            logger.error(f"Error handling system overload: {e}")
        finally:
            db.close()

    async def _handle_container_overload(self, container):
        """Handle container resource overload."""
        try:
            container_name = container.name
            logger.warning(f"Container {container_name} resources overloaded")

            # Extract lab and VM IDs from container name
            # Format: lab-{lab_id}-{vm_name}
            parts = container_name.split("-")
            if len(parts) >= 2:
                lab_id = int(parts[1])
                db = SessionLocal()
                lab = get_lab(db, lab_id)
                if lab:
                    # Update VM status
                    for vm in lab.vms:
                        if vm.docker_container_id == container.id:
                            update_vm(db, vm.id, {
                                "status": LabStatus.WARNING,
                                "vm_config": {
                                    "warning": "Resource overload detected"
                                }
                            })
                            break
                db.close()

        except Exception as e:
            logger.error(f"Error handling container overload: {e}")

    async def _cleanup_expired_labs(self):
        """Cleanup expired lab environments."""
        try:
            db = SessionLocal()
            expired_labs = (
                db.query(Lab)
                .filter(
                    Lab.expires_at <= datetime.utcnow(),
                    Lab.status != LabStatus.TERMINATED
                )
                .all()
            )

            for lab in expired_labs:
                logger.info(f"Cleaning up expired lab {lab.id}")
                await lab_manager.cleanup_lab(lab.id)

        except Exception as e:
            logger.error(f"Error cleaning up expired labs: {e}")
        finally:
            db.close()

    def _calculate_container_cpu_percent(self, stats: Dict) -> float:
        """Calculate container CPU usage percentage."""
        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                   stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                      stats["precpu_stats"]["system_cpu_usage"]
        if system_delta > 0:
            return (cpu_delta / system_delta) * 100.0
        return 0.0

    def _calculate_container_memory_percent(self, stats: Dict) -> float:
        """Calculate container memory usage percentage."""
        usage = stats["memory_stats"]["usage"]
        limit = stats["memory_stats"]["limit"]
        if limit > 0:
            return (usage / limit) * 100.0
        return 0.0

# Create singleton instance
resource_monitor = ResourceMonitor()
