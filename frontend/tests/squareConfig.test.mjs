import assert from 'node:assert/strict';
import test from 'node:test';

import {
  SQUARE_SDK_URLS,
  getSquareConfig
} from '../src/services/squareConfig.js';

const sandbox = {
  VITE_SQUARE_ENVIRONMENT: 'sandbox',
  VITE_SQUARE_APPLICATION_ID: 'sandbox-sq0idb-test-app',
  VITE_SQUARE_LOCATION_ID: 'test-location'
};

const production = {
  VITE_SQUARE_ENVIRONMENT: 'production',
  VITE_SQUARE_APPLICATION_ID: 'sq0idp-production-app',
  VITE_SQUARE_LOCATION_ID: 'production-location'
};

test('sandbox uses only the sandbox SDK and exposes sandbox guidance state', () => {
  assert.deepEqual(getSquareConfig(sandbox), {
    environment: 'sandbox',
    applicationId: sandbox.VITE_SQUARE_APPLICATION_ID,
    locationId: sandbox.VITE_SQUARE_LOCATION_ID,
    sdkUrl: SQUARE_SDK_URLS.sandbox,
    sandbox: true
  });
});

test('production uses only the production SDK and hides sandbox guidance state', () => {
  assert.deepEqual(getSquareConfig(production), {
    environment: 'production',
    applicationId: production.VITE_SQUARE_APPLICATION_ID,
    locationId: production.VITE_SQUARE_LOCATION_ID,
    sdkUrl: SQUARE_SDK_URLS.production,
    sandbox: false
  });
});

test('environment is explicit and allowlisted', () => {
  assert.throws(() => getSquareConfig({}), /explicitly set/);
  assert.throws(
    () => getSquareConfig({ ...sandbox, VITE_SQUARE_ENVIRONMENT: 'staging' }),
    /sandbox or production/
  );
});

test('application ID cannot select a different environment', () => {
  assert.throws(
    () => getSquareConfig({
      ...sandbox,
      VITE_SQUARE_APPLICATION_ID: production.VITE_SQUARE_APPLICATION_ID
    }),
    /does not match/
  );
  assert.throws(
    () => getSquareConfig({
      ...production,
      VITE_SQUARE_APPLICATION_ID: sandbox.VITE_SQUARE_APPLICATION_ID
    }),
    /does not match/
  );
});

test('missing or placeholder credentials fail closed', () => {
  assert.throws(
    () => getSquareConfig({ ...sandbox, VITE_SQUARE_LOCATION_ID: '' }),
    /not configured/
  );
  assert.throws(
    () => getSquareConfig({
      ...sandbox,
      VITE_SQUARE_APPLICATION_ID: 'sandbox-sq0idb-your-app-id'
    }),
    /not configured/
  );
});
