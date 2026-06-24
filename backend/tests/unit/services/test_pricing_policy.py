from decimal import Decimal

from server.services.pricing_service import SinalitePricingStrategy


class DummyRepository:
    def get_cached_pricing(self, *args, **kwargs):
        return None

    def cache_pricing(self, *args, **kwargs):
        return None

    def get_cached_variants(self, *args, **kwargs):
        return None

    def cache_variants(self, *args, **kwargs):
        return None


class DummySinalite:
    def get_price_by_key(self, product_id, option_key):
        return [{'price': 100}]

    def get_product_variants(self, product_id, offset=0):
        return []

    def get_product_price(self, product_id, store_code, product_options):
        return [{'price': 95.5, 'packageInfo': {'fallback': 'direct-price'}}]


class TestPricingPolicy:
    def test_apply_retail_pricing_adds_fx_buffer_and_markup(self, app):
        app.config['PRICING_CAD_TO_USD_RATE'] = 0.75
        app.config['PRICING_EXCHANGE_BUFFER_PERCENT'] = 5
        app.config['PRICING_MARKUP_PERCENT'] = 30
        app.config['PRICING_FIXED_FEE_USD'] = 3
        app.config['PRICING_MINIMUM_PROFIT_USD'] = 0
        app.config['PRICING_ROUNDING_INCREMENT'] = '0.05'

        strategy = SinalitePricingStrategy(DummySinalite(), DummyRepository())

        with app.app_context():
            result = strategy._apply_retail_pricing(100, [5, 447])

        assert result['currency'] == 'USD'
        assert result['pricingBreakdown']['vendorBasePrice'] == 100.0
        assert result['pricingBreakdown']['convertedCost'] == 75.0
        assert result['pricingBreakdown']['bufferedCost'] == 78.75
        assert result['pricingBreakdown']['landedCost'] == 81.75
        assert result['pricingBreakdown']['markupPercent'] == 30.0
        assert result['price'] == 116.8
        assert result['pricingBreakdown']['retailPrice'] == 116.8
        assert len(result['pricingBreakdown']['explanation']) >= 4

    def test_calculate_price_uses_raw_option_key_for_sinalite_lookup(self, app):
        repository = DummyRepository()
        sinalite = DummySinalite()
        strategy = SinalitePricingStrategy(sinalite, repository)

        with app.app_context():
            result = strategy.calculate_price(14983, [176, 5, 18], 6, {'serviceLevel': 'none'})

        assert result is not None
        assert result['productOptions'] == [176, 5, 18]

    def test_calculate_price_falls_back_to_variant_lookup_when_pricebykey_fails(self, app):
        repository = DummyRepository()
        sinalite = DummySinalite()
        sinalite.get_price_by_key = lambda product_id, option_key: None
        sinalite.get_product_variants = lambda product_id, offset=0: [
            {'key': '141-217-451', 'price': 42.25}
        ]

        strategy = SinalitePricingStrategy(sinalite, repository)

        with app.app_context():
            result = strategy.calculate_price(122, [451, 141, 217], 6, {'serviceLevel': 'none'})

        assert result is not None
        assert result['pricingBreakdown']['vendorBasePrice'] == 42.25

    def test_calculate_price_falls_back_to_direct_price_endpoint_when_variant_lookup_fails(self, app):
        repository = DummyRepository()
        sinalite = DummySinalite()
        sinalite.get_price_by_key = lambda product_id, option_key: None
        sinalite.get_product_variants = lambda product_id, offset=0: []
        sinalite.get_product_price = lambda product_id, store_code, product_options: [
            {'price': 88.4, 'packageInfo': {'source': 'direct-price-endpoint'}}
        ]

        strategy = SinalitePricingStrategy(sinalite, repository)

        with app.app_context():
            result = strategy.calculate_price(57, [177], 6, {'serviceLevel': 'none'})

        assert result is not None
        assert result['pricingBreakdown']['vendorBasePrice'] == 88.4
        assert result['packageInfo']['source'] == 'direct-price-endpoint'

    def test_apply_retail_pricing_handles_nan_vendor_price(self, app):
        strategy = SinalitePricingStrategy(DummySinalite(), DummyRepository())

        with app.app_context():
            result = strategy._apply_retail_pricing('NaN', [177], customization={'serviceLevel': 'none'})

        assert result is not None
        assert result['pricingBreakdown']['vendorBasePrice'] == 0.0
        assert result['price'] >= 0.0

    def test_apply_retail_pricing_handles_nan_markup_percent(self, app):
        strategy = SinalitePricingStrategy(DummySinalite(), DummyRepository())
        app.config['PRICING_MARKUP_PERCENT'] = float('nan')

        with app.app_context():
            result = strategy._apply_retail_pricing(100, [177], customization={'serviceLevel': 'none'})

        assert result is not None
        assert result['pricingBreakdown']['markupPercent'] == 0.0
        assert result['price'] >= 0.0

    def test_apply_retail_pricing_recovers_from_invalid_policy_values(self, app):
        strategy = SinalitePricingStrategy(DummySinalite(), DummyRepository())
        original_get_policy = strategy._get_pricing_policy

        strategy._get_pricing_policy = lambda: {
            'vendor_currency': 'CAD',
            'display_currency': 'USD',
            'cad_to_usd_rate': 'bad-rate',
            'exchange_buffer_percent': 'bad-buffer',
            'markup_percent': 'bad-markup',
            'markup_ratio': Decimal('NaN'),
            'fixed_fee_usd': 'bad-fee',
            'minimum_profit_usd': 'bad-min-profit',
            'rounding_increment': 'bad-rounding',
            'customization_fees': {'none': Decimal('0')},
        }

        with app.app_context():
            result = strategy._apply_retail_pricing(100, [177], customization={'serviceLevel': 'none'})

        strategy._get_pricing_policy = original_get_policy

        assert result is not None
        assert result['price'] >= 0.0
        assert result['pricingBreakdown']['vendorBasePrice'] == 100.0
