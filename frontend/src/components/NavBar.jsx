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
  Chip
} from '@mui/material';
import { 
  AccountCircle, 
  Login, 
  PersonAdd, 
  Logout, 
  AdminPanelSettings,
  ShoppingCart
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import logo from '../assets/logo.png';
import CartIcon from '../pages/Shop/components/CartIcon';

const Navbar = () => {
  const { isAuthenticated, currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);

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

  return (
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

        {/* Navbar Links */}
        <Stack direction="row" spacing={2} alignItems="center">
          <Button
            component={Link}
            to="/"
            sx={{
              color: 'white',
              '&:hover': { color: (theme) => theme.palette.secondary.main },
            }}
          >
            Shop
          </Button>
          
          {/* Admin Button - Only show for Admin users */}
          {isAuthenticated && currentUser?.role === 'Admin' && (
            <Button
              onClick={handleAdminClick}
              startIcon={<AdminPanelSettings />}
              sx={{
                color: 'white',
                '&:hover': { color: (theme) => theme.palette.secondary.main },
              }}
            >
              Admin
            </Button>
          )}

          {/* Cart Icon */}
          <CartIcon />

          {/* Authentication Section */}
          {isAuthenticated ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                label={currentUser?.role || 'User'}
                size="small"
                color="secondary"
                variant="outlined"
                sx={{ color: 'white', borderColor: 'white' }}
              />
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
                <MenuItem onClick={handleLogout}>
                  <Logout sx={{ mr: 1 }} />
                  Logout
                </MenuItem>
              </Menu>
            </Box>
          ) : (
            <Stack direction="row" spacing={1}>
              <Button
                component={Link}
                to="/login"
                startIcon={<Login />}
                variant="outlined"
                sx={{
                  color: 'white',
                  borderColor: 'white',
                  '&:hover': { 
                    borderColor: (theme) => theme.palette.secondary.main,
                    color: (theme) => theme.palette.secondary.main 
                  },
                }}
              >
                Login
              </Button>
              <Button
                component={Link}
                to="/register"
                startIcon={<PersonAdd />}
                variant="contained"
                sx={{
                  backgroundColor: (theme) => theme.palette.secondary.main,
                  '&:hover': { 
                    backgroundColor: (theme) => theme.palette.secondary.dark 
                  },
                }}
              >
                Sign Up
              </Button>
            </Stack>
          )}
        </Stack>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;