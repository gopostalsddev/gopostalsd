/**
 * Layout Component for Go Postal SD Frontend
 * 
 * This component provides the main layout structure including the navbar and footer.
 */

import React from 'react';
import { Box } from '@mui/material';
import Navbar from './NavBar';
import Footer from './Footer';

const Layout = ({ children, showFooter = true }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1,
          pt: 8, // Account for fixed navbar height
          minHeight: 'calc(100vh - 64px)' // Ensure minimum height
        }}
      >
        {children}
      </Box>
      {showFooter && <Footer />}
    </Box>
  );
};

export default Layout;
