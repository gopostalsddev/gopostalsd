import React from "react";
import { Box, CircularProgress } from "@mui/material";

const SpinnerOverlay = ({ loading }) => {
  if (!loading) return null; // Only render when loading is true

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        position: "fixed", // Covers the viewport
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        backgroundColor: "rgba(0, 0, 0, 0.4)", // Semi-transparent overlay
        zIndex: 999, // Ensures it's above other content
      }}
    >
      <CircularProgress color="primary" />
    </Box>
  );
};

export default SpinnerOverlay;