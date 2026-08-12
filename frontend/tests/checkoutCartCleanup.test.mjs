import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const checkout = fs.readFileSync(
  new URL('../src/components/Checkout.jsx', import.meta.url),
  'utf8'
);
const context = fs.readFileSync(
  new URL('../src/contexts/CartContext.jsx', import.meta.url),
  'utf8'
);

test('successful checkout resets local cart state without a second server delete', () => {
  assert.match(checkout, /clearCartAfterCheckout\(\)/);
  assert.doesNotMatch(checkout, /await clearEntireCart\(\)/);
  assert.match(context, /const clearLocalCart = \(\) =>/);
  assert.match(context, /dispatch\(\{ type: CART_ACTIONS\.CLEAR_CART \}\)/);
});

test('authenticated cart operations retain bearer and CSRF authentication', () => {
  assert.doesNotMatch(context, /skipAuth:\s*true/);
});
