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
  LocalShipping,
  Inventory2,
  ArrowForward
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ width: '100%' }}>
      <Box
        sx={{
          width: '100%',
          background:
            'radial-gradient(circle at 12% 18%, rgba(182,73,38,0.32), transparent 28%), radial-gradient(circle at 88% 70%, rgba(255,255,255,0.12), transparent 24%), linear-gradient(160deg, #091421 0%, #0a2f4a 62%, #143a54 100%)',
          color: 'white',
          py: { xs: 7, md: 11 },
          borderBottom: '1px solid rgba(255,255,255,0.16)'
        }}
      >
        <Container maxWidth="xl">
          <Box sx={{ maxWidth: 960, mx: 'auto', textAlign: 'center' }}>
            <Chip
              label="Little Italy, San Diego"
              sx={{
                mb: 2.5,
                backgroundColor: 'rgba(255,255,255,0.2)',
                color: 'white',
                borderRadius: 1,
                border: '1px solid rgba(255,255,255,0.26)'
              }}
            />

            <Typography
              variant="h2"
              fontWeight={700}
              sx={{
                fontSize: { xs: '2.25rem', md: '4.25rem' },
                lineHeight: 1.03,
                mb: 1.8
              }}
            >
              Welcome To Go Postal SD
            </Typography>

            <Typography
              variant="h5"
              sx={{
                fontSize: { xs: '1.08rem', md: '1.45rem' },
                opacity: 0.96,
                mb: 3.5
              }}
            >
              Your Premier Shipping And Printing Destination in Little Italy, San Diego
            </Typography>

            <Stack
              direction="row"
              spacing={1.2}
              justifyContent="center"
              flexWrap="wrap"
              useFlexGap
              sx={{ mb: 4.5 }}
            >
              <Chip label="We Pick" sx={{ borderRadius: 1, fontWeight: 700, color: 'white', backgroundColor: 'rgba(9,20,33,0.5)' }} />
              <Chip label="We Pack" sx={{ borderRadius: 1, fontWeight: 700, color: 'white', backgroundColor: 'rgba(9,20,33,0.5)' }} />
              <Chip label="We Ship" sx={{ borderRadius: 1, fontWeight: 700, color: 'white', backgroundColor: 'rgba(9,20,33,0.5)' }} />
            </Stack>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.8} justifyContent="center">
              <Button
                variant="contained"
                size="large"
                endIcon={<ArrowForward />}
                onClick={() => navigate('/shop')}
                sx={{ borderRadius: 1, px: 4.5, py: 1.35, backgroundColor: 'secondary.main', '&:hover': { backgroundColor: 'secondary.dark' } }}
              >
                Place Order Online
              </Button>
              <Button
                variant="outlined"
                size="large"
                startIcon={<LocationOn />}
                href="https://maps.google.com/?q=1501+India+St+Suite+103+San+Diego+CA+92101"
                target="_blank"
                rel="noopener noreferrer"
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
                Visit In Person
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
                  Shipping Confidence
                </Typography>
                <Typography color="text.secondary" sx={{ lineHeight: 1.8 }}>
                  Get practical help with packing, pickup strategy, and shipping execution so your items move safely and predictably.
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
                  Local Accountability
                </Typography>
                <Typography color="text.secondary" sx={{ lineHeight: 1.8 }}>
                  Family-owned service means responsive support, transparent communication, and real help when your project has deadlines.
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
                  Premier copy, print, and document services for San Diego.
                </Typography>
                <Typography sx={{ lineHeight: 1.85, mb: 1.8 }}>
                  Go Postal is your premier destination for shipping and printing services in Little Italy, San Diego, CA. Conveniently located at <strong>1501 India St Suite 103, San Diego, CA</strong>, our family-owned business is dedicated to providing exceptional customer service and professional printing excellence.
                </Typography>
                <Typography sx={{ lineHeight: 1.85, mb: 1.8 }}>
                  We prioritize saving you time and money by offering the right printing services at competitive prices. Whether you need small black-and-white copies or large full-color prints, we handle everything with precision and care.
                </Typography>
                <Typography sx={{ lineHeight: 1.85 }}>
                  As San Diego's premier copy, print, and document services center, we handle everything from small black-and-white copies to large full-color prints. <strong>If it can be printed, Go Postal can do it!</strong>
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
                  Online convenience with in-person support.
                </Typography>
                <Typography sx={{ lineHeight: 1.9, color: 'text.secondary', mb: 2.4 }}>
                  Place printing orders online or in person. Our convenient online ordering system allows you to submit your printing jobs from anywhere, while our in-person service provides immediate assistance and consultation for your printing needs. Support local business and experience why shopping small means getting the best printing service around!
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
                    startIcon={<LocationOn />}
                    href="https://maps.google.com/?q=1501+India+St+Suite+103+San+Diego+CA+92101"
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{ borderRadius: 1 }}
                  >
                    Open Directions
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
