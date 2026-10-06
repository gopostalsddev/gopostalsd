import React, { createContext, useContext, useState } from 'react';

const ArtworkContext = createContext(null);

export function ArtworkProvider({ children }) {
  const [artworkFile, setArtworkFile] = useState(null);

  const clearArtwork = () => setArtworkFile(null);

  return (
    <ArtworkContext.Provider value={{ artworkFile, setArtworkFile, clearArtwork }}>
      {children}
    </ArtworkContext.Provider>
  );
}

export function useArtwork() {
  const ctx = useContext(ArtworkContext);
  if (!ctx) throw new Error('useArtwork must be used inside ArtworkProvider');
  return ctx;
}
