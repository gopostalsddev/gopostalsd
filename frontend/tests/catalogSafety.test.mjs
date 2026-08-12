import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const shop = fs.readFileSync(
  new URL('../src/pages/Shop/ShopPage.jsx', import.meta.url),
  'utf8'
);
const service = fs.readFileSync(
  new URL('../src/services/product_service.js', import.meta.url),
  'utf8'
);

test('public shop never invokes administrative catalog synchronization', () => {
  assert.doesNotMatch(shop, /syncPrintProductCategories/);
  assert.doesNotMatch(shop, /fetchPrintProductCategories/);
  assert.match(shop, /fetchEnabledPrintProductCategories/);
});

test('category fetch and synchronization failures propagate to callers', () => {
  const categoryFetch = service.match(
    /export const fetchPrintProductCategories[\s\S]*?\n};/
  )?.[0];
  const enabledFetch = service.match(
    /export const fetchEnabledPrintProductCategories[\s\S]*?\n};/
  )?.[0];
  const categorySync = service.match(
    /export const syncPrintProductCategories[\s\S]*?\n};/
  )?.[0];

  assert.match(categoryFetch, /throw error/);
  assert.match(enabledFetch, /throw error/);
  assert.match(categorySync, /throw error/);
});
