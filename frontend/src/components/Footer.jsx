import React from 'react';
import { Box, Typography } from '@mui/material';

const Footer = () => {
  return (
    <Box
      sx={{
        width: '100%',
        padding: '1rem',
        textAlign: 'center',
        borderTop: 'solid 2px #ccc',
        backgroundColor: '#eee',
        marginTop: 'auto', // Push footer to the bottom when content is short
      }}
    >
      <Typography variant="body2">
        © {new Date().getFullYear()} Uzima Prints. All rights reserved. Powered by Go Postal.
      </Typography>
    </Box>
  );
};

export default Footer;
