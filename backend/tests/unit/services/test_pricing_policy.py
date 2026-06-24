from server.services.pricing_service import SinalitePricingStrategy


class DummyRepository:
    def get_cached_pricing(self, *args, **kwargs):
        return None

    def cache_pricing(self, *args, **kwargs):
        return None


class DummySinalite:
    def get_price_by_key(self, product_id, option_key):
        return [{'price': 100}]


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
