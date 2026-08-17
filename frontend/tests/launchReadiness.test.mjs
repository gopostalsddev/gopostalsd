import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const read = (relativePath) => fs.readFileSync(
  new URL(relativePath, import.meta.url),
  'utf8'
);

const gallery = read('../src/pages/Gallery/GalleryPage.jsx');
const footer = read('../src/components/ProfessionalFooter.jsx');
const productDetail = read('../src/pages/Shop/components/ProductDetailPage.jsx');
const index = read('../index.html');
const robots = read('../public/robots.txt');

test('project ideas cannot be mistaken for client case studies', () => {
  assert.match(gallery, /They are not client case studies/);
  assert.match(gallery, /Planning example/);
  assert.doesNotMatch(gallery, /Showcase concept/);
  assert.doesNotMatch(gallery, /Little Italy Restaurant Launch Kit/);
});

test('footer does not render social controls without approved destinations', () => {
  assert.doesNotMatch(footer, /aria-label="Facebook"/);
  assert.doesNotMatch(footer, /aria-label="Twitter"/);
  assert.doesNotMatch(footer, /aria-label="Instagram"/);
  assert.doesNotMatch(footer, /aria-label="LinkedIn"/);
});

test('storefront has hostname-independent discovery metadata', () => {
  assert.match(index, /name="description"/);
  assert.match(index, /property="og:title"/);
  assert.match(index, /name="twitter:card"/);
  assert.match(robots, /User-agent: \*/);
  assert.doesNotMatch(index, /rel="canonical"/);
  assert.doesNotMatch(robots, /^Sitemap:/m);
});

test('artwork flow never claims a browser-selected file was uploaded', () => {
  assert.doesNotMatch(productDetail, /type="file"/);
  assert.doesNotMatch(productDetail, /Uploaded Artwork/);
  assert.match(productDetail, /secure artwork transfer/);
  assert.match(productDetail, /artworkHandoffAccepted/);
});
