import { createTheme } from "@mui/material";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#0B4A6F",
      light: "#3C7392",
      dark: "#082F49",
    },
    secondary: {
      main: "#B64926",
      light: "#D36D47",
      dark: "#7D2E16",
    },
    success: {
      main: "#2F6F4F",
    },
    info: {
      main: "#2563EB",
    },
    warning: {
      main: "#C2410C",
    },
    background: {
      default: "#F4EFE7",
      paper: "#FFFDF9",
    },
    text: {
      primary: "#18212A",
      secondary: "#5A6470",
    },
  },
  typography: {
    fontFamily: '"Space Grotesk", "Avenir Next", "Segoe UI", sans-serif',
    h1: {
      fontFamily: '"Iowan Old Style", Georgia, serif',
      fontWeight: 700,
      letterSpacing: '-0.04em',
    },
    h2: {
      fontFamily: '"Iowan Old Style", Georgia, serif',
      fontWeight: 700,
      letterSpacing: '-0.04em',
    },
    h3: {
      fontFamily: '"Iowan Old Style", Georgia, serif',
      fontWeight: 700,
      letterSpacing: '-0.03em',
    },
    h4: {
      fontFamily: '"Iowan Old Style", Georgia, serif',
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h5: {
      fontFamily: '"Iowan Old Style", Georgia, serif',
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    button: {
      fontWeight: 700,
      letterSpacing: '0.01em',
      textTransform: 'none',
    },
    overline: {
      fontWeight: 700,
      letterSpacing: '0.18em',
    },
  },
  breakpoints: {
    values: {
      xs: 0, // Extra small devices (mobile)
      sm: 600, // Small devices (tablet)
      md: 960, // Medium devices (small laptop)
      lg: 1280, // Large devices (desktop)
      xl: 1920, // Extra large devices (big screens)
    },
  },
  mixins: {
    toolbar: {
      minHeight: 64, // Default navbar height
      "@media (max-width:600px)": {
        minHeight: 56, // Smaller height for mobile
      },
    },
  },
  shape: {
    borderRadius: 18,
  },
  shadows: [
    'none',
    '0 12px 26px rgba(24, 33, 42, 0.08)',
    '0 14px 30px rgba(24, 33, 42, 0.10)',
    '0 18px 34px rgba(24, 33, 42, 0.12)',
    '0 20px 38px rgba(24, 33, 42, 0.14)',
    '0 24px 42px rgba(24, 33, 42, 0.15)',
    '0 28px 46px rgba(24, 33, 42, 0.16)',
    '0 32px 50px rgba(24, 33, 42, 0.17)',
    '0 36px 54px rgba(24, 33, 42, 0.18)',
    '0 40px 58px rgba(24, 33, 42, 0.19)',
    '0 44px 62px rgba(24, 33, 42, 0.20)',
    '0 48px 66px rgba(24, 33, 42, 0.21)',
    '0 52px 70px rgba(24, 33, 42, 0.22)',
    '0 56px 74px rgba(24, 33, 42, 0.23)',
    '0 60px 78px rgba(24, 33, 42, 0.24)',
    '0 64px 82px rgba(24, 33, 42, 0.25)',
    '0 68px 86px rgba(24, 33, 42, 0.26)',
    '0 72px 90px rgba(24, 33, 42, 0.27)',
    '0 76px 94px rgba(24, 33, 42, 0.28)',
    '0 80px 98px rgba(24, 33, 42, 0.29)',
    '0 84px 102px rgba(24, 33, 42, 0.30)',
    '0 88px 106px rgba(24, 33, 42, 0.31)',
    '0 92px 110px rgba(24, 33, 42, 0.32)',
    '0 96px 114px rgba(24, 33, 42, 0.33)',
    '0 100px 118px rgba(24, 33, 42, 0.34)',
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 999,
          paddingInline: 22,
          boxShadow: 'none',
        },
        contained: {
          boxShadow: '0 14px 30px rgba(24, 33, 42, 0.14)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 999,
          fontWeight: 700,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontWeight: 700,
          color: '#3A4652',
        },
      },
    },
  },
});

export default theme;