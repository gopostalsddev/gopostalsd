import React from 'react';
import { AppBar, Toolbar, Box, Typography, Stack, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import logo from '../assets/logo.png';
import CartIcon from '../pages/Shop/components/CartIcon';

const Navbar = () => {
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
        <Box sx={{ display: 'flex', alignItems: 'center', marginRight: '1rem' }}>
          <img src={logo} alt="GoPostal SD Logo" style={{ height: '62px', width: 'auto' }} />
        </Box>

        {/* App Name */}
        <Typography variant="h6" sx={{ flexGrow: 1, userSelect: 'none' }}>
          PRINTING
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
          <Button
            component={Link}
            to="/admin"
            sx={{
              color: 'white',
              '&:hover': { color: (theme) => theme.palette.secondary.main },
            }}
          >
            Admin
          </Button>
          <CartIcon />
        </Stack>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;