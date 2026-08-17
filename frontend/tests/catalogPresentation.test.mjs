import assert from 'node:assert/strict';
import test from 'node:test';

import {
  filterCatalogCategories,
  normalizeCatalogCategoryName,
  prepareCatalogCategories,
} from '../src/utils/catalogCategories.js';

test('trailing vendor separators normalize without changing ordinary names', () => {
  assert.equal(
    normalizeCatalogCategoryName('Coroplast Signs & Yard Signs-'),
    normalizeCatalogCategoryName('Coroplast Signs & Yard Signs')
  );
  assert.equal(normalizeCatalogCategoryName('A-Frame Signs'), 'a-frame signs');
});

test('public catalog deterministically removes display duplicates', () => {
  const categories = [
    { id: 2, name: 'Pull Up Banners-', image: 'duplicate.jpg' },
    { id: 1, name: 'Pull Up Banners', image: null },
    { id: 3, name: 'Business Cards' },
  ];

  assert.deepEqual(
    prepareCatalogCategories(categories).map(({ id, name }) => ({ id, name })),
    [
      { id: 3, name: 'Business Cards' },
      { id: 1, name: 'Pull Up Banners' },
    ]
  );
  assert.deepEqual(
    prepareCatalogCategories([...categories].reverse()).map(({ id, name }) => ({ id, name })),
    [
      { id: 3, name: 'Business Cards' },
      { id: 1, name: 'Pull Up Banners' },
    ]
  );
});

test('catalog search covers names and descriptions after deduplication', () => {
  const categories = [
    { id: 1, name: 'Flyers', description: 'Promotional handouts' },
    { id: 2, name: 'Business Cards', description: 'Professional cards' },
  ];

  assert.deepEqual(
    filterCatalogCategories(categories, 'promo').map((category) => category.id),
    [1]
  );
  assert.deepEqual(
    filterCatalogCategories(categories, '').map((category) => category.id),
    [2, 1]
  );
});
