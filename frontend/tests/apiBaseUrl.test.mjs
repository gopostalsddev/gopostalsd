import assert from 'node:assert/strict'
import test from 'node:test'

import { getApiBaseUrl } from '../src/services/apiBaseUrl.js'


test('explicit API base URL is normalized and preserved', () => {
  assert.equal(
    getApiBaseUrl({ VITE_API_BASE_URL: 'https://api.example.test/api/' }),
    'https://api.example.test/api',
  )
})


test('production defaults to the same-origin API path', () => {
  assert.equal(getApiBaseUrl({ DEV: false }), '/api')
})


test('development also uses the Vite-proxied same-origin API path', () => {
  assert.equal(getApiBaseUrl({ DEV: true }), '/api')
})
