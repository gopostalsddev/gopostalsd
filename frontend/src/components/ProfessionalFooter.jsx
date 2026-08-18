import {
  Box,
  Container,
  Grid,
  Typography,
  Link,
  Divider,
  Stack
} from '@mui/material';
import { Email } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/uzima-mark.svg';

const ProfessionalFooter = () => {
  const navigate = useNavigate();

  const currentYear = new Date().getFullYear();

  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <Box
      component="footer"
      sx={{
        background: 'linear-gradient(45deg, rgb(0, 0, 0), rgb(7, 59, 102))',
        color: 'white',
        py: 4,
        mt: 'auto'
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4}>
          {/* Company Info */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Box sx={{ mb: 3 }}>
              <img 
                src={logo} 
                alt="Uzima Prints logo"
                style={{ height: '60px', width: 'auto' }}
              />
            </Box>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Uzima Prints
            </Typography>
          </Grid>

          {/* Quick Links */}
          <Grid size={{ xs: 12, sm: 6, md: 2 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Quick Links
            </Typography>
            <Stack spacing={1}>
              <Link
                component="button"
                variant="body2"
                onClick={() => handleNavigation('/services')}
                sx={{ 
                  color: 'white', 
                  textAlign: 'left',
                  '&:hover': { 
                    backgroundColor: 'rgba(255,255,255,0.1)',
                    color: 'white'
                  }
                }}
              >
                Services
              </Link>
              <Link
                component="button"
                variant="body2"
                onClick={() => handleNavigation('/shop')}
                sx={{ 
                  color: 'white', 
                  textAlign: 'left',
                  '&:hover': { 
                    backgroundColor: 'rgba(255,255,255,0.1)',
                    color: 'white'
                  }
                }}
              >
                Shop
              </Link>
              <Link
                component="button"
                variant="body2"
                onClick={() => handleNavigation('/contact')}
                sx={{ 
                  color: 'white', 
                  textAlign: 'left',
                  '&:hover': { 
                    backgroundColor: 'rgba(255,255,255,0.1)',
                    color: 'white'
                  }
                }}
              >
                Contact
              </Link>
              <Link
                component="button"
                variant="body2"
                onClick={() => handleNavigation('/gallery')}
                sx={{ 
                  color: 'white', 
                  textAlign: 'left',
                  '&:hover': { 
                    backgroundColor: 'rgba(255,255,255,0.1)',
                    color: 'white'
                  }
                }}
              >
                Project Ideas
              </Link>
              <Link
                component="button"
                variant="body2"
                onClick={() => handleNavigation('/faqs')}
                sx={{ 
                  color: 'white', 
                  textAlign: 'left',
                  '&:hover': { 
                    backgroundColor: 'rgba(255,255,255,0.1)',
                    color: 'white'
                  }
                }}
              >
                FAQs
              </Link>
            </Stack>
          </Grid>

          {/* Contact Info */}
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Contact Info
            </Typography>
            <Stack spacing={1}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Email sx={{ mr: 1, fontSize: 20 }} />
                <Link 
                  href="mailto:support@uzimaprints.com"
                  sx={{ color: 'white', textDecoration: 'none' }}
                >
                  support@uzimaprints.com
                </Link>
              </Box>
            </Stack>
          </Grid>

          {/* Store Hours */}
          <Grid size={{ xs: 12, md: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Store Hours
            </Typography>
            <Stack spacing={0.5}>
              <Typography variant="body2">Mon - Fri: 9:00 AM - 6:00 PM</Typography>
              <Typography variant="body2">Saturday: 10:00 AM - 2:00 PM</Typography>
              <Typography variant="body2">Sunday: Closed</Typography>
            </Stack>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3, backgroundColor: 'rgba(255,255,255,0.2)' }} />

        {/* Bottom Section */}
        <Box sx={{ 
          display: 'flex', 
          flexDirection: { xs: 'column', md: 'row' }, 
          justifyContent: 'space-between', 
          alignItems: 'center',
          gap: 2
        }}>
          <Box>
            <Typography variant="body2" color="rgba(255,255,255,0.8)">
              © {currentYear} Uzima Prints. All rights reserved.
            </Typography>
            <Typography variant="caption" color="rgba(255,255,255,0.58)">
              Powered by Go Postal
            </Typography>
          </Box>

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
            <Link
              component="button"
              variant="body2"
              onClick={() => handleNavigation('/terms')}
              sx={{ color: 'rgba(255,255,255,0.8)' }}
            >
              Terms
            </Link>
            <Link
              component="button"
              variant="body2"
              onClick={() => handleNavigation('/privacy')}
              sx={{ color: 'rgba(255,255,255,0.8)' }}
            >
              Privacy
            </Link>
          </Stack>
        </Box>
      </Container>
    </Box>
  );
};

export default ProfessionalFooter;
