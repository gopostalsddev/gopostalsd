export const SQUARE_SDK_URLS = Object.freeze({
  sandbox: 'https://sandbox.web.squarecdn.com/v1/square.js',
  production: 'https://web.squarecdn.com/v1/square.js'
});

const APPLICATION_ID_PREFIX = Object.freeze({
  sandbox: 'sandbox-sq0idb-',
  production: 'sq0idp-'
});

const PLACEHOLDER_APP_ID = 'sandbox-sq0idb-your-app-id';
const PLACEHOLDER_LOCATION_ID = 'your-location-id';

export function getSquareConfig(env) {
  const environment = env.VITE_SQUARE_ENVIRONMENT?.trim().toLowerCase();
  const applicationId = env.VITE_SQUARE_APPLICATION_ID?.trim();
  const locationId = env.VITE_SQUARE_LOCATION_ID?.trim();

  if (!Object.hasOwn(SQUARE_SDK_URLS, environment)) {
    throw new Error(
      'VITE_SQUARE_ENVIRONMENT must be explicitly set to sandbox or production.'
    );
  }
  if (
    !applicationId ||
    applicationId === PLACEHOLDER_APP_ID ||
    !locationId ||
    locationId === PLACEHOLDER_LOCATION_ID
  ) {
    throw new Error('Square application and location credentials are not configured.');
  }
  if (!applicationId.startsWith(APPLICATION_ID_PREFIX[environment])) {
    throw new Error(
      'VITE_SQUARE_APPLICATION_ID does not match VITE_SQUARE_ENVIRONMENT.'
    );
  }

  return {
    environment,
    applicationId,
    locationId,
    sdkUrl: SQUARE_SDK_URLS[environment],
    sandbox: environment === 'sandbox'
  };
}
