import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Paper,
  Button,
  Box,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  VpnKey as VpnKeyIcon,
  Timer as TimerIcon,
  Stop as StopIcon,
  DesktopWindows as DesktopIcon,
} from '@mui/icons-material';
import { VPNConfigDialog } from './VPNConfigDialog';
import { VMAccess } from './VMAccess';

enum LabStatus {
  CREATING = 'CREATING',
  RUNNING = 'RUNNING',
  STOPPED = 'STOPPED',
  FAILED = 'FAILED',
}

export interface Lab {
  id: number;
  name: string;
  status: LabStatus;
  expires_at: string;
  access?: {
    vpn_config?: string;
    ssh_commands?: Record<string, string>;
    rdp_commands?: Record<string, string>;
    custom_access?: Record<string, any>;
  };
  vms?: Array<{
    name: string;
    os: string;
    ip: string;
    terminal_enabled: boolean;
    rdp_enabled: boolean;
  }>;
}

// Mock data for testing
const mockLabs: Lab[] = [
  {
    id: 1,
    name: "Web Application Security Lab",
    status: LabStatus.RUNNING,
    expires_at: new Date(Date.now() + 3600000).toISOString(),
    access: {
      vpn_config: "client\ndev tun\nproto udp\nremote vpn.lab.local 1194\n...",
      ssh_commands: {
        "Web Server": "ssh -i lab_key.pem user@10.0.0.1",
        "Database Server": "ssh -i lab_key.pem user@10.0.0.2"
      },
      rdp_commands: {
        "Windows Client": "10.0.0.3:3389"
      }
    },
    vms: [
      {
        name: "Kali Linux Attack Box",
        os: "Kali Linux 2023.3",
        ip: "10.0.0.100",
        terminal_enabled: true,
        rdp_enabled: true
      },
      {
        name: "Vulnerable Web Server",
        os: "Ubuntu 22.04",
        ip: "10.0.0.10",
        terminal_enabled: true,
        rdp_enabled: false
      },
      {
        name: "Windows Target",
        os: "Windows Server 2019",
        ip: "10.0.0.20",
        terminal_enabled: true,
        rdp_enabled: true
      }
    ]
  },
  {
    id: 2,
    name: "Network Security Lab",
    status: LabStatus.CREATING,
    expires_at: new Date(Date.now() + 7200000).toISOString(),
    vms: [
      {
        name: "Kali Linux Attack Box",
        os: "Kali Linux 2023.3",
        ip: "10.0.1.100",
        terminal_enabled: true,
        rdp_enabled: true
      },
      {
        name: "Target Network Router",
        os: "VyOS 1.4",
        ip: "10.0.1.1",
        terminal_enabled: true,
        rdp_enabled: false
      },
      {
        name: "Internal Windows Server",
        os: "Windows Server 2022",
        ip: "172.16.0.10",
        terminal_enabled: true,
        rdp_enabled: true
      }
    ]
  }
];

export const LabManager: React.FC = () => {
  const [labs, setLabs] = useState<Lab[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLab, setSelectedLab] = useState<Lab | null>(null);
  const [vpnDialogOpen, setVpnDialogOpen] = useState(false);
  const [vmAccessOpen, setVmAccessOpen] = useState(false);
  const [extendDialogOpen, setExtendDialogOpen] = useState(false);
  const [extendTime, setExtendTime] = useState(1);

  const fetchLabs = async () => {
    try {
      setLoading(true);
      // In a real application, this would be an API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setLabs(mockLabs);
      // Simulate lab creation completion after 5 seconds
      const creatingLab = mockLabs.find(lab => lab.status === LabStatus.CREATING);
      if (creatingLab) {
        setTimeout(() => {
          setLabs(prevLabs => 
            prevLabs.map(lab => 
              lab.id === creatingLab.id 
                ? {
                    ...lab,
                    status: LabStatus.RUNNING,
                    access: {
                      vpn_config: "client\ndev tun\nproto udp\nremote vpn.lab.local 1194\n...",
                      ssh_commands: {
                        "Kali Linux": "ssh -i lab_key.pem kali@10.0.0.10",
                        "Target Host": "ssh -i lab_key.pem user@10.0.0.20"
                      },
                      rdp_commands: {
                        "Windows Target": "10.0.0.30:3389"
                      }
                    }
                  }
                : lab
            )
          );
        }, 5000);
      }
    } catch (err) {
      setError('Failed to fetch labs');
      console.error('Error fetching labs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLabs();
  }, []);

  const handleStopLab = async (labId: number) => {
    try {
      // In a real application, this would be an API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setLabs(labs.map(lab => 
        lab.id === labId ? { ...lab, status: LabStatus.STOPPED } : lab
      ));
    } catch (err) {
      console.error('Error stopping lab:', err);
      setError('Failed to stop lab');
    }
  };

  const handleExtendTime = async () => {
    try {
      const labToExtend = selectedLab;
      if (!labToExtend) return;

      // In a real application, this would be an API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setLabs(prevLabs => 
        prevLabs.map(lab => 
          lab.id === labToExtend.id 
            ? {
                ...lab,
                expires_at: new Date(new Date(lab.expires_at).getTime() + (extendTime * 3600000)).toISOString()
              }
            : lab
        )
      );
      setExtendDialogOpen(false);
      setSelectedLab(null);
    } catch (err) {
      console.error('Error extending lab time:', err);
      setError('Failed to extend lab time');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom sx={{ my: 4 }}>
        My Labs
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {labs.map((lab) => (
          <Grid item xs={12} md={6} key={lab.id}>
            <Paper
              sx={{
                p: 3,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <Typography variant="h6" gutterBottom>
                {lab.name}
              </Typography>

              <Box sx={{ flex: 1 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Status: {lab.status}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Expires: {new Date(lab.expires_at).toLocaleString()}
                </Typography>

                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => {
                      setSelectedLab(lab);
                      setVmAccessOpen(true);
                    }}
                    startIcon={<DesktopIcon />}
                    disabled={lab.status !== LabStatus.RUNNING}
                    sx={{ mr: 1, mb: 1 }}
                  >
                    Access VMs
                  </Button>

                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={() => {
                      setSelectedLab(lab);
                      setVpnDialogOpen(true);
                    }}
                    startIcon={<VpnKeyIcon />}
                    disabled={lab.status !== LabStatus.RUNNING}
                    sx={{ mr: 1, mb: 1 }}
                  >
                    VPN Config
                  </Button>

                  <Button
                    variant="outlined"
                    color="primary"
                    startIcon={<TimerIcon />}
                    onClick={() => {
                      setSelectedLab(lab);
                      setExtendDialogOpen(true);
                    }}
                    disabled={lab.status !== LabStatus.RUNNING}
                    sx={{ mr: 1, mb: 1 }}
                  >
                    Extend Time
                  </Button>

                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={<StopIcon />}
                    onClick={() => handleStopLab(lab.id)}
                    disabled={lab.status !== LabStatus.RUNNING}
                    sx={{ mb: 1 }}
                  >
                    Stop Lab
                  </Button>
                </Box>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <VPNConfigDialog
        open={vpnDialogOpen}
        lab={selectedLab}
        onClose={() => {
          setVpnDialogOpen(false);
          setSelectedLab(null);
        }}
      />

      <VMAccess
        open={vmAccessOpen}
        lab={selectedLab}
        onClose={() => {
          setVmAccessOpen(false);
          setSelectedLab(null);
        }}
      />

      {/* Extend Time Dialog */}
      <Dialog open={extendDialogOpen} onClose={() => setExtendDialogOpen(false)}>
        <DialogTitle>Extend Lab Time</DialogTitle>
        <DialogContent>
          <Box sx={{ p: 2 }}>
            <Typography variant="body1" gutterBottom>
              Current expiration: {selectedLab ? new Date(selectedLab.expires_at).toLocaleString() : ''}
            </Typography>
            <TextField
              label="Hours to extend"
              type="number"
              value={extendTime}
              onChange={(e) => setExtendTime(Math.max(1, parseInt(e.target.value) || 1))}
              InputProps={{ inputProps: { min: 1 } }}
              fullWidth
              sx={{ mt: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExtendDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleExtendTime} variant="contained" color="primary">
            Extend
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};
