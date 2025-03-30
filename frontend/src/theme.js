import { createTheme } from "@mui/material";

const theme = createTheme({
  palette: {
    type: "light",
    primary: {
      main: "#011d37",
      light: "#334A5F",
      dark: "#001426",
    },
    secondary: {
      main: "#f50057",
      light: "#F73378",
      dark: "#AB003C",
    },
    background: {
      default: "#fafafa",
      paper: "#e0f7fa",
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
});

export default theme;