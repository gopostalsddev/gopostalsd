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
const authContext = read('../src/contexts/AuthContext.jsx');
const registerPage = read('../src/pages/Auth/RegisterPage.jsx');
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

test('storefront discovery metadata uses the confirmed Uzima Prints origin', () => {
  assert.match(index, /name="description"/);
  assert.match(index, /property="og:title"/);
  assert.match(index, /name="twitter:card"/);
  assert.match(robots, /User-agent: \*/);
  assert.match(index, /rel="canonical" href="https:\/\/uzimaprints\.com\/"/);
  assert.match(index, /property="og:site_name" content="Uzima Prints"/);
  assert.match(robots, /^Sitemap: https:\/\/uzimaprints\.com\/sitemap\.xml$/m);
});

test('customer-facing launch identity is Uzima Prints with restrained platform attribution', () => {
  assert.match(footer, /© \{currentYear\} Uzima Prints/);
  assert.match(footer, /Powered by Go Postal/);
  assert.match(footer, /support@uzimaprints\.com/);
  assert.doesNotMatch(footer, /gopostalsd@gmail\.com|1501 India St|619-237-0374/);
});

test('artwork flow never claims a browser-selected file was uploaded', () => {
  assert.doesNotMatch(productDetail, /type="file"/);
  assert.doesNotMatch(productDetail, /Uploaded Artwork/);
  assert.match(productDetail, /secure artwork transfer/);
  assert.match(productDetail, /artworkHandoffAccepted/);
});

test('registration password validation has a stable callback and ignores stale responses', () => {
  assert.match(authContext, /const validatePassword = useCallback\(async \(password\) =>/);
  assert.match(authContext, /const clearError = useCallback\(\(\) =>/);
  assert.match(registerPage, /let cancelled = false/);
  assert.match(registerPage, /if \(!cancelled && result\.success\)/);
  assert.match(registerPage, /cancelled = true/);
});

test('registration failures preserve machine-readable error codes for visible handling', () => {
  assert.match(authContext, /return \{ success: false, error: registrationError \}/);
  assert.match(registerPage, /result\.error\?\.code === 'USER_EXISTS'/);
  assert.doesNotMatch(registerPage, /result\.error && result\.error\.code/);
});
