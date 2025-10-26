/**
 * Home Page for Go Postal SD Frontend
 * 
 * Professional home page showcasing Go Postal's services and information.
 */

import React from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Stack,
  Chip
} from '@mui/material';
import {
  Print,
  LocationOn,
  Business
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ width: '100%' }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, rgb(0, 0, 0), rgb(7, 59, 102))',
          color: 'white',
          py: { xs: 8, md: 12 },
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={8}>
              <Typography 
                variant="h2" 
                fontWeight="bold" 
                gutterBottom
                sx={{ 
                  fontSize: { xs: '2.5rem', md: '3.5rem' },
                  textShadow: '2px 2px 4px rgba(0,0,0,0.2)'
                }}
              >
                Welcome To Go Postal SD
              </Typography>
              <Typography 
                variant="h5" 
                sx={{ mb: 4, opacity: 0.95 }}
              >
                Your Premier Shipping And Printing Destination in Little Italy, San Diego
              </Typography>
              <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
                <Chip 
                  label="We Pick" 
                  sx={{ 
                    backgroundColor: 'rgb(42 87 148)', 
                    color: 'white',
                    fontWeight: 'bold'
                  }} 
                />
                <Chip 
                  label="We Pack" 
                  sx={{ 
                    backgroundColor: 'rgb(42 87 148)', 
                    color: 'white',
                    fontWeight: 'bold'
                  }} 
                />
                <Chip 
                  label="We Ship" 
                  sx={{ 
                    backgroundColor: 'rgb(42 87 148)', 
                    color: 'white',
                    fontWeight: 'bold'
                  }} 
                />
                <Chip 
                  label="We Print"
                  onClick={() => navigate('/shop')}
                  sx={{ 
                    // backgroundColor: 'rgba(211, 47, 47, 0.9)',
                    color: 'white',
                    fontWeight: 'bold',
                    backgroundColor: 'secondary.main',
                    '&:hover': {
                      backgroundColor: 'secondary.dark'
                    }
                  }} 
                />
              </Stack>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Business 
                  sx={{ 
                    fontSize: { xs: '120px', md: '180px' }, 
                    opacity: 0.3,
                    color: 'white'
                  }} 
                />
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Container maxWidth="lg" sx={{ py: 8 }}>
        {/* Call to Action Section */}
        <Box 
          sx={{ 
            textAlign: 'center',
            background: 'linear-gradient(to bottom right, rgba(25, 118, 210, 0.08), rgba(211, 47, 47, 0.08))',
            borderRadius: 4,
            p: 6,
            mb: 8
          }}
        >
          
          <Typography 
            variant="h6" 
            color="text.secondary" 
            sx={{ mb: 4 }}
          >
            Place your printing order online or visit us in person!
          </Typography>
          <Stack 
            direction={{ xs: 'column', sm: 'row' }} 
            spacing={2} 
            justifyContent="center"
            sx={{ gap: 2 }}
          >
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/shop')}
              startIcon={<Print />}
              sx={{ 
                px: 6, 
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 'bold',
                backgroundColor: 'secondary.main',
                '&:hover': {
                  backgroundColor: 'secondary.dark'
                }
              }}
            >
              Order Online
            </Button>
            <Button
              variant="outlined"
              size="large"
              href="https://maps.google.com/?q=1501+India+St+Suite+103+San+Diego+CA+92101"
              target="_blank"
              rel="noopener noreferrer"
              startIcon={<LocationOn />}
              sx={{ 
                px: 6, 
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 'bold',
                borderWidth: 2,
                borderColor: 'rgb(7, 59, 102)',
                color: 'rgb(7, 59, 102)',
                '&:hover': {
                  borderWidth: 2,
                  borderColor: 'rgb(7, 59, 102)',
                  backgroundColor: 'rgba(7, 59, 102, 0.1)'
                }
              }}
            >
              Visit In Person
            </Button>
          </Stack>
        </Box>

        {/* About Section */}
        <Box sx={{ mb: 8 }}>
          <Typography 
            variant="h3" 
            gutterBottom 
            color="primary" 
            fontWeight="bold"
            align="center"
            sx={{ mb: 4 }}
          >
            About Us
          </Typography>
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.8 }}>
                Go Postal is your premier destination for shipping and printing services in Little Italy, San Diego, CA. 
                Conveniently located at <strong>1501 India St Suite 103, San Diego, CA</strong>, our family-owned business is dedicated to providing 
                exceptional customer service and professional printing excellence.
              </Typography>
              <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.8 }}>
                We prioritize saving you time and money by offering the right printing services at competitive prices. 
                Whether you need small black-and-white copies or large full-color prints, we handle everything with precision and care.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.8 }}>
                As San Diego's premier copy, print, and document services center, we handle everything from small black-and-white copies 
                to large full-color prints. <strong>If it can be printed, Go Postal can do it!</strong>
              </Typography>
              <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.8 }}>
                Place printing orders online or in person. Our convenient online ordering system allows you to submit your printing 
                jobs from anywhere, while our in-person service provides immediate assistance and consultation for your printing needs. 
                Support local business and experience why shopping small means getting the best printing service around!
              </Typography>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </Box>
  );
};

export default HomePage;
