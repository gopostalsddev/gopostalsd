import React, { useState } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Box, 
  Typography, 
  Stack, 
  Button, 
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Divider,
  Chip,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { 
  AccountCircle, 
  ManageAccounts,
  Login, 
  Logout, 
  AdminPanelSettings,
  ShoppingCart,
  Menu as MenuIcon,
  Close,
  Home,
  Store,
  ContactMail,
  ReceiptLong
} from '@mui/icons-material';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { CartIcon } from './CartIcon';
import logo from '../assets/logo.png';

const Navbar = () => {
  const { isAuthenticated, user: currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleMenuClose();
    navigate('/');
  };

  const handleAdminClick = () => {
    if (isAuthenticated && currentUser?.role === 'Admin') {
      navigate('/admin');
    } else {
      navigate('/unauthorized');
    }
    handleMenuClose();
  };

  const handleMobileMenuToggle = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const handleMobileMenuClose = () => {
    setMobileMenuOpen(false);
  };

  const handleMobileNavigation = (path) => {
    navigate(path);
    handleMobileMenuClose();
  };

  return (
    <>
      <AppBar
        sx={{
          background: 'linear-gradient(45deg,rgb(0, 0, 0),rgb(7, 59, 102))',
          position: 'fixed',
          top: 0,
          width: '100%',
          borderBottom: 'solid 2px #ccc',
          zIndex: 1000,
        }}
      >
        <Toolbar>
          {/* Logo */}
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              marginRight: '1rem',
              cursor: 'pointer'
            }}
            onClick={() => navigate('/')}
          >
            <img src={logo} alt="GoPostal SD Logo" style={{ height: '62px', width: 'auto' }} />
          </Box>

          {/* App Name */}
          <Typography 
            variant="h6" 
            sx={{ 
              flexGrow: 1, 
              userSelect: 'none',
              cursor: 'pointer'
            }}
            onClick={() => navigate('/')}
          >
            GO POSTAL SD
          </Typography>

          {/* Desktop Navigation */}
          {!isMobile && (
            <Stack direction="row" spacing={2} alignItems="center">
              <Button
                component={Link}
                to="/"
                startIcon={<Home />}
                sx={{
                  color: 'white',
                  fontWeight: location.pathname === '/' ? 'bold' : 'normal',
                  borderBottom: location.pathname === '/' ? '3px solid white' : '3px solid transparent',
                  '&:hover': { 
                    backgroundColor: (theme) => theme.palette.primary.dark,
                    color: 'white'
                  },
                }}
              >
                Home
              </Button>
              <Button
                component={Link}
                to="/shop"
                startIcon={<Store />}
                sx={{
                  color: 'white',
                  fontWeight: location.pathname === '/shop' ? 'bold' : 'normal',
                  borderBottom: location.pathname === '/shop' ? '3px solid white' : '3px solid transparent',
                  '&:hover': { 
                    backgroundColor: (theme) => theme.palette.primary.dark,
                    color: 'white'
                  },
                }}
              >
                Shop
              </Button>
              <Button
                component={Link}
                to="/contact"
                startIcon={<ContactMail />}
                sx={{
                  color: 'white',
                  fontWeight: location.pathname === '/contact' ? 'bold' : 'normal',
                  borderBottom: location.pathname === '/contact' ? '3px solid white' : '3px solid transparent',
                  '&:hover': { 
                    backgroundColor: (theme) => theme.palette.primary.dark,
                    color: 'white'
                  },
                }}
              >
                Contact
              </Button>
              
              {/* Admin Button - Only show for Admin users */}
              {isAuthenticated && currentUser?.role === 'Admin' && (
                <Button
                  onClick={handleAdminClick}
                  startIcon={<AdminPanelSettings />}
                  sx={{
                    color: 'white',
                    '&:hover': { 
                      backgroundColor: (theme) => theme.palette.primary.dark,
                      color: 'white'
                    },
                  }}
                >
                  Admin
                </Button>
              )}

              {/* Cart Icon */}
              <CartIcon onClick={() => navigate('/cart')} />

              {/* Authentication Section */}
              {isAuthenticated ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" sx={{ color: 'white', fontWeight: 500 }}>
                    {currentUser?.first_name && currentUser?.last_name 
                      ? `${currentUser.first_name} ${currentUser.last_name}`
                      : currentUser?.email?.split('@')[0] || 'User'
                    }
                  </Typography>
                  <IconButton
                    onClick={handleMenuOpen}
                    sx={{ color: 'white' }}
                    aria-label="account menu"
                  >
                    <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                      {currentUser?.first_name?.charAt(0) || <AccountCircle />}
                    </Avatar>
                  </IconButton>
                  
                  <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleMenuClose}
                    anchorOrigin={{
                      vertical: 'bottom',
                      horizontal: 'right',
                    }}
                    transformOrigin={{
                      vertical: 'top',
                      horizontal: 'right',
                    }}
                  >
                    <MenuItem disabled>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {currentUser?.first_name} {currentUser?.last_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {currentUser?.email}
                        </Typography>
                      </Box>
                    </MenuItem>
                    <Divider />
                    <MenuItem onClick={() => { handleMenuClose(); navigate('/account'); }}>
                      <ManageAccounts sx={{ mr: 1 }} />
                      My Account
                    </MenuItem>
                    <MenuItem onClick={() => { handleMenuClose(); navigate('/track-order'); }}>
                      <ReceiptLong sx={{ mr: 1 }} />
                      Track Orders
                    </MenuItem>
                    {currentUser?.role === 'Admin' && (
                      <MenuItem onClick={() => { handleMenuClose(); navigate('/admin'); }}>
                        <AdminPanelSettings sx={{ mr: 1 }} />
                        Admin Panel
                      </MenuItem>
                    )}
                    <MenuItem onClick={handleLogout}>
                      <Logout sx={{ mr: 1 }} />
                      Logout
                    </MenuItem>
                  </Menu>
                </Box>
              ) : (
                <Button
                  component={Link}
                  to="/login"
                  startIcon={<Login />}
                  variant="outlined"
                  sx={{
                    color: 'white',
                    borderColor: 'white',
                    '&:hover': { 
                      backgroundColor: (theme) => theme.palette.primary.dark,
                      borderColor: (theme) => theme.palette.primary.dark,
                      color: 'white'
                    },
                  }}
                >
                  Login
                </Button>
              )}
            </Stack>
          )}

          {/* Mobile Navigation */}
          {isMobile && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CartIcon onClick={() => navigate('/cart')} />
              <IconButton
                onClick={handleMobileMenuToggle}
                sx={{ color: 'white' }}
                aria-label="mobile menu"
              >
                {mobileMenuOpen ? <Close /> : <MenuIcon />}
              </IconButton>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer Menu */}
      <Drawer
        anchor="right"
        open={mobileMenuOpen}
        onClose={handleMobileMenuClose}
        sx={{
          '& .MuiDrawer-paper': {
            width: 280,
            backgroundColor: 'background.paper',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <img 
              src={logo} 
              alt="Go Postal SD Logo" 
              style={{ height: '50px', width: 'auto' }}
            />
            <IconButton onClick={handleMobileMenuClose}>
              <Close />
            </IconButton>
          </Box>

          <List>
            <ListItem disablePadding>
              <ListItemButton onClick={() => handleMobileNavigation('/')}>
                <ListItemIcon>
                  <Home />
                </ListItemIcon>
                <ListItemText primary="Home" />
              </ListItemButton>
            </ListItem>
            
            <ListItem disablePadding>
              <ListItemButton onClick={() => handleMobileNavigation('/shop')}>
                <ListItemIcon>
                  <Store />
                </ListItemIcon>
                <ListItemText primary="Shop" />
              </ListItemButton>
            </ListItem>
            
            <ListItem disablePadding>
              <ListItemButton onClick={() => handleMobileNavigation('/contact')}>
                <ListItemIcon>
                  <ContactMail />
                </ListItemIcon>
                <ListItemText primary="Contact" />
              </ListItemButton>
            </ListItem>

            {isAuthenticated && currentUser?.role === 'Admin' && (
              <ListItem disablePadding>
                <ListItemButton onClick={() => handleMobileNavigation('/admin')}>
                  <ListItemIcon>
                    <AdminPanelSettings />
                  </ListItemIcon>
                  <ListItemText primary="Admin" />
                </ListItemButton>
              </ListItem>
            )}

            <Divider sx={{ my: 2 }} />

            {isAuthenticated ? (
              <>
                <ListItem disablePadding>
                  <ListItemButton disabled>
                    <ListItemIcon>
                      <AccountCircle />
                    </ListItemIcon>
                    <ListItemText 
                      primary={`${currentUser?.first_name} ${currentUser?.last_name}`}
                      secondary={currentUser?.email}
                    />
                  </ListItemButton>
                </ListItem>

                  <ListItem disablePadding>
                    <ListItemButton onClick={() => handleMobileNavigation('/account')}>
                      <ListItemIcon>
                        <ManageAccounts />
                      </ListItemIcon>
                      <ListItemText primary="My Account" />
                    </ListItemButton>
                  </ListItem>

                  <ListItem disablePadding>
                    <ListItemButton onClick={() => handleMobileNavigation('/track-order')}>
                      <ListItemIcon>
                        <ReceiptLong />
                      </ListItemIcon>
                      <ListItemText primary="Track Orders" />
                    </ListItemButton>
                  </ListItem>
                
                <ListItem disablePadding>
                  <ListItemButton onClick={handleLogout}>
                    <ListItemIcon>
                      <Logout />
                    </ListItemIcon>
                    <ListItemText primary="Logout" />
                  </ListItemButton>
                </ListItem>
              </>
            ) : (
              <ListItem disablePadding>
                <ListItemButton onClick={() => handleMobileNavigation('/login')}>
                  <ListItemIcon>
                    <Login />
                  </ListItemIcon>
                  <ListItemText primary="Login" />
                </ListItemButton>
              </ListItem>
            )}
          </List>
        </Box>
      </Drawer>
    </>
  );
};

export default Navbar;