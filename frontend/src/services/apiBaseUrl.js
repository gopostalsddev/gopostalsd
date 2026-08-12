const normalizeBase = (value) => {
  if (!value) {
    return '';
  }
  return value.endsWith('/') ? value.slice(0, -1) : value;
};

export const getApiBaseUrl = (environment = import.meta.env) => {
  const envBaseUrl = normalizeBase(environment.VITE_API_BASE_URL);
  if (envBaseUrl) {
    return envBaseUrl;
  }

  if (environment.DEV) {
    return '/api';
  }

  // Production launches behind one public origin with /api reverse-proxied to
  // Flask. A deliberately configured VITE_API_BASE_URL may override this for a
  // split-origin rehearsal; no historical provider hostname is inferred.
  return '/api';
};
