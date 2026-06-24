import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './main.css'
import App from './App.jsx'
import { ThemeProvider } from '@mui/material/styles'
import { CssBaseline } from '@mui/material';
import theme from './theme.js'

// Suppress debug logs in production builds.
// console.error is kept so genuine runtime errors still surface.
if (!import.meta.env.DEV) {
  /* eslint-disable no-console */
  console.log  = () => {};
  console.warn = () => {};
  console.info = () => {};
  console.debug = () => {};
  /* eslint-enable no-console */
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
    <CssBaseline />
    <App />
    </ThemeProvider>
  </StrictMode>,
)
