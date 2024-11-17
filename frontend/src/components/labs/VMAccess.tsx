import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Tabs,
  Tab,
  Typography,
  Paper,
  IconButton,
  CircularProgress,
} from '@mui/material';
import {
  Terminal as TerminalIcon,
  DesktopWindows as DesktopIcon,
  OpenInNew as OpenInNewIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

// Import Lab type from LabManager
import { Lab } from './LabManager';

interface VM {
  name: string;
  os: string;
  ip: string;
  terminal_enabled: boolean;
  rdp_enabled: boolean;
}

interface VMAccessProps {
  open: boolean;
  lab: Lab | null;
  onClose: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`vm-access-tabpanel-${index}`}
      aria-labelledby={`vm-access-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 2 }}>{children}</Box>}
    </div>
  );
}

export const VMAccess: React.FC<VMAccessProps> = ({ open, lab, onClose }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleOpenWebTerminal = (vmName: string) => {
    if (!lab) return;
    // In a real implementation, this would open a web-based terminal
    // using a service like ttyd, wetty, or Apache Guacamole
    window.open(`/terminal/${lab.id}/${vmName}`, '_blank');
  };

  const handleOpenWebRDP = (vmName: string) => {
    if (!lab) return;
    // In a real implementation, this would open a web-based RDP client
    // using a service like Apache Guacamole or noVNC
    window.open(`/rdp/${lab.id}/${vmName}`, '_blank');
  };

  const handleRefreshVM = async (vmName: string) => {
    if (!lab) return;
    try {
      setLoading(true);
      // In a real implementation, this would make an API call to refresh the VM
      await new Promise(resolve => setTimeout(resolve, 2000));
    } catch (error) {
      console.error('Failed to refresh VM:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!lab || !lab.vms) {
    return null;
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>Virtual Machine Access - {lab.name}</DialogTitle>
      <DialogContent>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab icon={<TerminalIcon />} label="Terminal Access" />
            <Tab icon={<DesktopIcon />} label="Remote Desktop" />
          </Tabs>
        </Box>

        {/* Terminal Access */}
        <TabPanel value={activeTab} index={0}>
          <Typography variant="h6" gutterBottom>
            Web Terminal Access
          </Typography>
          {lab.vms?.filter(vm => vm.terminal_enabled).map((vm) => (
            <Paper key={vm.name} sx={{ p: 2, mb: 2 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="subtitle1">{vm.name}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    OS: {vm.os} | IP: {vm.ip}
                  </Typography>
                </Box>
                <Box>
                  <IconButton
                    onClick={() => handleRefreshVM(vm.name)}
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={24} /> : <RefreshIcon />}
                  </IconButton>
                  <IconButton
                    onClick={() => handleOpenWebTerminal(vm.name)}
                    color="primary"
                  >
                    <OpenInNewIcon />
                  </IconButton>
                </Box>
              </Box>
            </Paper>
          ))}
        </TabPanel>

        {/* Remote Desktop */}
        <TabPanel value={activeTab} index={1}>
          <Typography variant="h6" gutterBottom>
            Remote Desktop Access
          </Typography>
          {lab.vms?.filter(vm => vm.rdp_enabled).map((vm) => (
            <Paper key={vm.name} sx={{ p: 2, mb: 2 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="subtitle1">{vm.name}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    OS: {vm.os} | IP: {vm.ip}
                  </Typography>
                </Box>
                <Box>
                  <IconButton
                    onClick={() => handleRefreshVM(vm.name)}
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={24} /> : <RefreshIcon />}
                  </IconButton>
                  <IconButton
                    onClick={() => handleOpenWebRDP(vm.name)}
                    color="primary"
                  >
                    <OpenInNewIcon />
                  </IconButton>
                </Box>
              </Box>
            </Paper>
          ))}
        </TabPanel>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};
