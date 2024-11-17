import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  TextField,
  Tabs,
  Tab,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';

// Import Lab type from LabManager
import { Lab } from './LabManager';

interface VPNConfigDialogProps {
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
      id={`vpn-tabpanel-${index}`}
      aria-labelledby={`vpn-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export const VPNConfigDialog: React.FC<VPNConfigDialogProps> = ({
  open,
  lab,
  onClose,
}) => {
  const [tabValue, setTabValue] = useState(0);
  const [copied, setCopied] = useState(false);

  const handleCopyConfig = async (text: string | undefined) => {
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      alert('Configuration copied to clipboard!');
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const handleDownloadConfig = (filename: string, content: string | undefined) => {
    if (!content) return;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (!lab || !lab.access) {
    return null;
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>Access Configuration - {lab.name}</DialogTitle>
      <DialogContent>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="VPN Configuration" />
            {lab.access.ssh_commands && Object.keys(lab.access.ssh_commands).length > 0 && <Tab label="SSH Access" />}
            {lab.access.rdp_commands && Object.keys(lab.access.rdp_commands).length > 0 && <Tab label="RDP Access" />}
            {lab.access.custom_access && <Tab label="Custom Access" />}
          </Tabs>
        </Box>

        {/* VPN Configuration */}
        <TabPanel value={tabValue} index={0}>
          <Typography variant="subtitle2" gutterBottom>
            OpenVPN Configuration
          </Typography>
          <Box sx={{ position: 'relative' }}>
            <Box sx={{ position: 'absolute', right: 8, top: 8, zIndex: 1 }}>
              <Tooltip title="Copy configuration">
                <IconButton
                  onClick={() => handleCopyConfig(lab.access?.vpn_config)}
                  size="small"
                >
                  <CopyIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Download configuration">
                <IconButton
                  onClick={() => handleDownloadConfig(`lab_${lab.id}.ovpn`, lab.access?.vpn_config)}
                  size="small"
                >
                  <DownloadIcon />
                </IconButton>
              </Tooltip>
            </Box>
            <TextField
              multiline
              fullWidth
              rows={10}
              value={lab.access?.vpn_config || ''}
              InputProps={{
                readOnly: true,
              }}
            />
          </Box>
        </TabPanel>

        {/* SSH Access */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="subtitle2" gutterBottom>
            SSH Commands
          </Typography>
          {Object.entries(lab.access?.ssh_commands || {}).map(([name, command]) => (
            <Paper key={name} variant="outlined" sx={{ p: 2, mb: 2, position: 'relative' }}>
              <Box sx={{ position: 'absolute', right: 8, top: 8 }}>
                <Tooltip title="Copy command">
                  <IconButton
                    onClick={() => handleCopyConfig(command as string)}
                    size="small"
                  >
                    <CopyIcon />
                  </IconButton>
                </Tooltip>
              </Box>
              <Typography variant="subtitle2" gutterBottom>
                {name}
              </Typography>
              <TextField
                fullWidth
                value={command}
                InputProps={{
                  readOnly: true,
                }}
                variant="outlined"
                size="small"
              />
            </Paper>
          ))}
        </TabPanel>

        {/* RDP Access */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="subtitle2" gutterBottom>
            RDP Connection Details
          </Typography>
          {Object.entries(lab.access?.rdp_commands || {}).map(([name, address]) => (
            <Paper key={name} variant="outlined" sx={{ p: 2, mb: 2, position: 'relative' }}>
              <Box sx={{ position: 'absolute', right: 8, top: 8 }}>
                <Tooltip title="Copy address">
                  <IconButton
                    onClick={() => handleCopyConfig(address as string)}
                    size="small"
                  >
                    <CopyIcon />
                  </IconButton>
                </Tooltip>
              </Box>
              <Typography variant="subtitle2" gutterBottom>
                {name}
              </Typography>
              <TextField
                fullWidth
                value={address}
                InputProps={{
                  readOnly: true,
                }}
                variant="outlined"
                size="small"
              />
            </Paper>
          ))}
        </TabPanel>

        {/* Custom Access */}
        {lab.access.custom_access && (
          <TabPanel value={tabValue} index={3}>
            <Typography variant="subtitle2" gutterBottom>
              Custom Access Details
            </Typography>
            {Object.entries(lab.access.custom_access).map(([name, details]) => (
              <Paper key={name} variant="outlined" sx={{ p: 2, mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  {name}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Host: {(details as any).host}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Ports: {JSON.stringify((details as any).ports)}
                </Typography>
              </Paper>
            ))}
          </TabPanel>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};
