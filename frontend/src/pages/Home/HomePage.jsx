import React from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Stack
} from '@mui/material';
import {
  Print,
  ContactMail,
  LocalShipping,
  Inventory2,
  ArrowForward
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import heroImage from '../../assets/uzima-hero-bringing-ideas-to-life.png';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ width: '100%' }}>
      <Box
        sx={{
          width: '100%',
          backgroundColor: '#091421',
          backgroundImage: `linear-gradient(90deg, rgba(9,20,33,0.94) 0%, rgba(9,20,33,0.8) 48%, rgba(9,20,33,0.5) 100%), url(${heroImage})`,
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundSize: 'cover',
          color: 'white',
          py: { xs: 7, md: 11 },
          borderBottom: '1px solid rgba(255,255,255,0.16)'
        }}
      >
        <Container maxWidth="xl">
          <Box sx={{ maxWidth: 960, mx: 'auto', textAlign: 'center' }}>

            <Typography
              variant="h2"
              fontWeight={700}
              sx={{
                fontSize: { xs: '2.25rem', md: '4.25rem' },
                lineHeight: 1.03,
                mb: 1.8
              }}
            >
              Bring Your Ideas to Life with Uzima Prints
            </Typography>

            <Typography
              variant="h5"
              sx={{
                fontSize: { xs: '1.08rem', md: '1.45rem' },
                opacity: 0.96,
                mb: 3.5
              }}
            >
              Professional printing, simple online ordering, and dependable support.
            </Typography>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.8} justifyContent="center">
              <Button
                variant="contained"
                size="large"
                endIcon={<ArrowForward />}
                onClick={() => navigate('/shop')}
                sx={{
                  borderRadius: 1,
                  px: 4.5,
                  py: 1.35,
                  color: '#18212A',
                  backgroundColor: '#F5B942',
                  '&:hover': { backgroundColor: '#DFA52E' }
                }}
              >
                Place Order Online
              </Button>
              <Button
                variant="outlined"
                size="large"
                startIcon={<ContactMail />}
                onClick={() => navigate('/contact')}
                sx={{
                  borderRadius: 1,
                  px: 4.5,
                  py: 1.35,
                  color: 'white',
                  borderColor: 'rgba(255,255,255,0.76)',
                  '&:hover': {
                    borderColor: 'white',
                    backgroundColor: 'rgba(255,255,255,0.12)'
                  }
                }}
              >
                Talk to Our Team
              </Button>
            </Stack>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ py: { xs: 5, md: 7 } }}>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', md: 'repeat(3, minmax(0, 1fr))' },
            gap: 3
          }}
        >
          <Box>
            <Card elevation={0} sx={{ borderRadius: 1, border: '1px solid rgba(24,33,42,0.12)', height: '100%' }}>
              <CardContent sx={{ p: 3.2 }}>
                <LocalShipping color="primary" sx={{ mb: 1.2 }} />
                <Typography variant="h6" fontWeight={700} sx={{ mb: 1.1 }}>
                  Delivery Across the U.S. &amp; Canada
                </Typography>
                <Typography color="text.secondary" sx={{ lineHeight: 1.8 }}>
                  Uzima Prints ships finished print orders throughout the United States and Canada, with available delivery options and costs shown during checkout.
                </Typography>
              </CardContent>
            </Card>
          </Box>

          <Box>
            <Card elevation={0} sx={{ borderRadius: 1, border: '1px solid rgba(24,33,42,0.12)', height: '100%' }}>
              <CardContent sx={{ p: 3.2 }}>
                <Print color="primary" sx={{ mb: 1.2 }} />
                <Typography variant="h6" fontWeight={700} sx={{ mb: 1.1 }}>
                  Print Precision
                </Typography>
                <Typography color="text.secondary" sx={{ lineHeight: 1.8 }}>
                  From small black-and-white copies to large full-color runs, every order is handled with professional attention.
                </Typography>
              </CardContent>
            </Card>
          </Box>

          <Box>
            <Card elevation={0} sx={{ borderRadius: 1, border: '1px solid rgba(24,33,42,0.12)', height: '100%' }}>
              <CardContent sx={{ p: 3.2 }}>
                <Inventory2 color="primary" sx={{ mb: 1.2 }} />
                <Typography variant="h6" fontWeight={700} sx={{ mb: 1.1 }}>
                  Responsive Support
                </Typography>
                <Typography color="text.secondary" sx={{ lineHeight: 1.8 }}>
                  Clear communication and hands-on help keep your project moving when quality and deadlines matter.
                </Typography>
              </CardContent>
            </Card>
          </Box>
        </Box>
      </Container>

      <Container maxWidth="xl" sx={{ pb: { xs: 6, md: 8 } }}>
        <Grid container spacing={3}>
          <Grid size={{ xs: 12 }}>
            <Card elevation={0} sx={{ borderRadius: 1, border: '1px solid rgba(24,33,42,0.12)', height: '100%' }}>
              <CardContent sx={{ p: { xs: 3, md: 3.5 } }}>
                <Typography variant="overline" color="text.secondary" sx={{ letterSpacing: '0.12em' }}>
                  About Us
                </Typography>
                <Typography variant="h4" fontWeight={700} sx={{ mt: 1, mb: 2.2 }}>
                  Premier online shipping, printing, and document services.
                </Typography>
                <Typography sx={{ lineHeight: 1.85, mb: 1.8 }}>
                  Uzima Prints makes professional print ordering straightforward. Browse products, configure your order, and get responsive help when a project needs a human touch.
                </Typography>
                <Typography sx={{ lineHeight: 1.85, mb: 1.8 }}>
                  We prioritize saving you time and money by offering the right printing services at competitive prices. Whether you need small black-and-white copies or large full-color prints, we handle everything with precision and care.
                </Typography>
                <Typography sx={{ lineHeight: 1.85 }}>
                  From everyday business materials to high-impact promotional pieces, Uzima Prints helps turn finished ideas into print-ready results.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={{ xs: 12 }}>
            <Card
              elevation={0}
              sx={{
                borderRadius: 1,
                border: '1px solid rgba(24,33,42,0.12)',
                background:
                  'linear-gradient(165deg, rgba(244,239,231,0.9), rgba(255,255,255,0.92) 55%, rgba(182,73,38,0.09) 130%)',
                height: '100%'
              }}
            >
              <CardContent sx={{ p: { xs: 3, md: 3.5 }, height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Typography variant="overline" color="text.secondary" sx={{ letterSpacing: '0.12em' }}>
                  How To Order
                </Typography>
                <Typography variant="h4" fontWeight={700} sx={{ mt: 1, mb: 2.2 }}>
                  Online convenience with real support.
                </Typography>
                <Typography sx={{ lineHeight: 1.9, color: 'text.secondary', mb: 2.4 }}>
                  Place printing orders online from anywhere, then work with our team when artwork, product choices, or fulfillment details need clarification.
                </Typography>

                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.6} sx={{ mt: 'auto' }}>
                  <Button
                    variant="contained"
                    endIcon={<ArrowForward />}
                    onClick={() => navigate('/shop')}
                    sx={{ borderRadius: 1 }}
                  >
                    Start Printing Order
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<ContactMail />}
                    onClick={() => navigate('/contact')}
                    sx={{ borderRadius: 1 }}
                  >
                    Contact Support
                  </Button>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default HomePage;
