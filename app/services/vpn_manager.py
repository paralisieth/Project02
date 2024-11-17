import os
import asyncio
import logging
from typing import Dict, Optional
import aiofiles
import docker
from openvpn_api import VPNManager
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)
docker_client = docker.from_env()

class VPNServerManager:
    def __init__(self):
        self.vpn_config_dir = "/etc/openvpn/server"
        self.client_config_dir = "/etc/openvpn/client"
        self.vpn_manager = VPNManager("localhost", 7505)
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist."""
        os.makedirs(self.vpn_config_dir, exist_ok=True)
        os.makedirs(self.client_config_dir, exist_ok=True)

    async def create_vpn_server(self, lab_id: int) -> Optional[str]:
        """Create a new VPN server for a lab."""
        try:
            # Generate server configuration
            server_config = self._generate_server_config(lab_id)
            config_path = os.path.join(self.vpn_config_dir, f"lab_{lab_id}.conf")
            
            async with aiofiles.open(config_path, 'w') as f:
                await f.write(server_config)

            # Start OpenVPN container
            container = docker_client.containers.run(
                image="kylemanna/openvpn",
                name=f"vpn-lab-{lab_id}",
                detach=True,
                cap_add=["NET_ADMIN"],
                volumes={
                    self.vpn_config_dir: {
                        'bind': '/etc/openvpn',
                        'mode': 'rw'
                    }
                },
                ports={
                    '1194/udp': ('0.0.0.0', self._get_vpn_port(lab_id))
                },
                environment={
                    "VIRTUAL_PORT": "1194",
                    "VIRTUAL_PROTO": "udp"
                }
            )

            # Generate client configuration
            client_config = await self._generate_client_config(lab_id)
            return client_config

        except Exception as e:
            logger.error(f"Error creating VPN server for lab {lab_id}: {e}")
            return None

    async def cleanup_vpn_server(self, lab_id: int):
        """Cleanup VPN server resources."""
        try:
            # Stop and remove container
            container_name = f"vpn-lab-{lab_id}"
            try:
                container = docker_client.containers.get(container_name)
                container.stop(timeout=10)
                container.remove()
            except docker.errors.NotFound:
                pass

            # Remove configuration files
            server_config = os.path.join(self.vpn_config_dir, f"lab_{lab_id}.conf")
            client_config = os.path.join(self.client_config_dir, f"lab_{lab_id}.ovpn")
            
            if os.path.exists(server_config):
                os.remove(server_config)
            if os.path.exists(client_config):
                os.remove(client_config)

            logger.info(f"Cleaned up VPN server for lab {lab_id}")

        except Exception as e:
            logger.error(f"Error cleaning up VPN server for lab {lab_id}: {e}")

    def _generate_server_config(self, lab_id: int) -> str:
        """Generate OpenVPN server configuration."""
        port = self._get_vpn_port(lab_id)
        return f"""port {port}
proto udp
dev tun
ca ca.crt
cert server.crt
key server.key
dh dh.pem
server 10.{lab_id}.0.0 255.255.255.0
ifconfig-pool-persist ipp.txt
push "route {settings.LAB_VPN_SUBNET}"
keepalive 10 120
cipher AES-256-CBC
persist-key
persist-tun
status openvpn-status.log
verb 3"""

    async def _generate_client_config(self, lab_id: int) -> str:
        """Generate OpenVPN client configuration."""
        port = self._get_vpn_port(lab_id)
        client_config = f"""client
dev tun
proto udp
remote {settings.LAB_VPN_HOST} {port}
resolv-retry infinite
nobind
persist-key
persist-tun
cipher AES-256-CBC
verb 3
<ca>
{await self._read_file(os.path.join(self.vpn_config_dir, 'ca.crt'))}
</ca>
<cert>
{await self._read_file(os.path.join(self.client_config_dir, f'client_{lab_id}.crt'))}
</cert>
<key>
{await self._read_file(os.path.join(self.client_config_dir, f'client_{lab_id}.key'))}
</key>"""
        return client_config

    def _get_vpn_port(self, lab_id: int) -> int:
        """Get unique VPN port for lab."""
        return 1194 + lab_id  # Base VPN port + lab_id

    async def _read_file(self, path: str) -> str:
        """Read file content asynchronously."""
        try:
            async with aiofiles.open(path, 'r') as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return ""

    async def generate_certificates(self, lab_id: int):
        """Generate certificates for VPN server and client."""
        try:
            # Use easy-rsa to generate certificates
            os.system(f"""
                cd {self.vpn_config_dir}
                ./easyrsa init-pki
                ./easyrsa build-ca nopass
                ./easyrsa build-server-full server nopass
                ./easyrsa build-client-full client_{lab_id} nopass
                ./easyrsa gen-dh
            """)
        except Exception as e:
            logger.error(f"Error generating certificates for lab {lab_id}: {e}")
            raise

# Create singleton instance
vpn_manager = VPNServerManager()
