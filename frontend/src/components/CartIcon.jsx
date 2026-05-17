import React from 'react';
import {
  IconButton,
  Badge,
  Tooltip,
  Box,
  Typography
} from '@mui/material';
import {
  ShoppingCart as ShoppingCartIcon,
  Login as LoginIcon
} from '@mui/icons-material';
import { useCartOperations } from '../hooks/useCart';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export function CartIcon({ onClick }) {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { getCartStats } = useCartOperations();
  const cartStats = getCartStats();

  const handleClick = () => {
    if (!isAuthenticated) {
      navigate('/login');
    } else if (onClick) {
      onClick();
    }
  };

  return (
    <Tooltip title={isAuthenticated ? "Shopping Cart" : "Login to view cart"}>
      <IconButton
        color="inherit"
        onClick={handleClick}
        sx={{ position: 'relative' }}
      >
        <Badge
          badgeContent={isAuthenticated ? cartStats.totalItems : 0}
          color="error"
          invisible={!isAuthenticated || cartStats.totalItems === 0}
          sx={{
            '& .MuiBadge-badge': {
              fontSize: '0.75rem',
              minWidth: '18px',
              height: '18px'
            }
          }}
        >
          {isAuthenticated ? <ShoppingCartIcon /> : <LoginIcon />}
        </Badge>
      </IconButton>
    </Tooltip>
  );
}

export function CartSummary({ compact = false }) {
  const { getCartStats } = useCartOperations();
  const cartStats = getCartStats();

  if (compact) {
    return (
      <Box display="flex" alignItems="center" gap={1}>
        <ShoppingCartIcon fontSize="small" />
        <Box>
          <Typography variant="body2" color="text.secondary">
            {cartStats.totalItems} item{cartStats.totalItems !== 1 ? 's' : ''}
          </Typography>
          <Typography variant="body2" fontWeight="bold">
            ${cartStats.total.toFixed(2)}
          </Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="body2" color="text.secondary">
        Cart ({cartStats.totalItems} items)
      </Typography>
      <Typography variant="h6" color="primary">
        ${cartStats.total.toFixed(2)}
      </Typography>
    </Box>
  );
}
