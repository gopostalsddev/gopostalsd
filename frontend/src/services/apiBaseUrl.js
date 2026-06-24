const normalizeBase = (value) => {
  if (!value) {
    return '';
  }
  return value.endsWith('/') ? value.slice(0, -1) : value;
};

export const getApiBaseUrl = () => {
  const envBaseUrl = normalizeBase(import.meta.env.VITE_API_BASE_URL);
  if (envBaseUrl) {
    return envBaseUrl;
  }

  if (import.meta.env.DEV) {
    return '/api';
  }

  if (typeof window !== 'undefined') {
    const host = window.location.hostname;

    // Render production frontend is served on gopostalsd-website.onrender.com
    // while backend API is served on gopostalsd.onrender.com.
    if (host === 'gopostalsd-website.onrender.com') {
      return 'https://gopostalsd.onrender.com/api';
    }
  }

  return '/api';
};
