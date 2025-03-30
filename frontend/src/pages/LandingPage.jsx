import React from 'react';
import { Typography, Box } from '@mui/material';
import Navbar from '../components/NavBar';
import Footer from '../components/Footer';

const LandingPage = () => {
  return (
    <>
      <Navbar />
      <Box
        sx={{
          width: '100%',
          height: 'calc(100vh - 4rem)', // Adjust height to leave room for footer
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center',
        }}
      >
        <Typography variant="h2" component="h1" color="text.primary">
          Welcome
        </Typography>
      </Box>
      <Footer />
    </>
  );
};

export default LandingPage;
