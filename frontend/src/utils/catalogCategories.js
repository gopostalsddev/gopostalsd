const trailingSeparators = /[\s\-–—_]+$/u;

export const normalizeCatalogCategoryName = (name) => (
  String(name || '')
    .trim()
    .replace(trailingSeparators, '')
    .replace(/\s+/gu, ' ')
    .toLocaleLowerCase('en-US')
);

const categoryQuality = (category) => {
  const name = String(category?.name || '').trim();
  const classified = Number(
    category?.product_classification_status?.classified_products || 0
  );

  return (
    (trailingSeparators.test(name) ? 0 : 1000) +
    (category?.image ? 100 : 0) +
    (category?.description ? 10 : 0) +
    (Number.isFinite(classified) ? classified : 0)
  );
};

const candidateWins = (candidate, current) => {
  const qualityDifference = categoryQuality(candidate) - categoryQuality(current);
  if (qualityDifference !== 0) return qualityDifference > 0;

  return String(candidate?.id ?? '').localeCompare(
    String(current?.id ?? ''),
    'en-US',
    { numeric: true }
  ) < 0;
};

/**
 * Present an upstream vendor catalog safely without rewriting source data.
 *
 * Sinalite can return duplicate display categories that differ only by a
 * trailing separator. The public storefront should show one deterministic
 * representative while the administrator retains the original records for
 * deliberate catalog curation.
 */
export const prepareCatalogCategories = (categories) => {
  const selected = new Map();

  for (const category of Array.isArray(categories) ? categories : []) {
    const key = normalizeCatalogCategoryName(category?.name);
    if (!key) continue;

    const current = selected.get(key);
    if (!current || candidateWins(category, current)) {
      selected.set(key, category);
    }
  }

  return [...selected.values()].sort((left, right) => (
    String(left.name || '').localeCompare(String(right.name || ''), 'en-US', {
      sensitivity: 'base',
    })
  ));
};

export const filterCatalogCategories = (categories, query) => {
  const prepared = prepareCatalogCategories(categories);
  const normalizedQuery = String(query || '').trim().toLocaleLowerCase('en-US');
  if (!normalizedQuery) return prepared;

  return prepared.filter((category) => (
    String(category.name || '').toLocaleLowerCase('en-US').includes(normalizedQuery) ||
    String(category.description || '').toLocaleLowerCase('en-US').includes(normalizedQuery)
  ));
};
