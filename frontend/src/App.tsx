import React from 'react';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { LabManager } from './components/labs/LabManager';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <LabManager />
    </ThemeProvider>
  );
}

export default App;
