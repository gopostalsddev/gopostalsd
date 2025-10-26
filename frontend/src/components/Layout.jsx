/**
 * Layout Component for Go Postal SD Frontend
 * 
 * This component provides the main layout structure including the navbar and footer.
 */

import React from 'react';
import { Box } from '@mui/material';
import Navbar from './NavBar';
import ProfessionalFooter from './ProfessionalFooter';

const Layout = ({ children, showFooter = true }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Box 
        component="main" 
        sx={{ 
          flex: 1,
          pt: 8, // Account for fixed navbar height
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {children}
      </Box>
      {showFooter && <ProfessionalFooter />}
    </Box>
  );
};

export default Layout;
