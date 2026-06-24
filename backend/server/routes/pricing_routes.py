"""
Pricing Routes for Go Postal SD Application

This module defines all pricing-related API endpoints using Flask-RESTX.
It follows the same pattern as print_product_routes.py.
"""

from flask_restx import Namespace, Resource, fields
from flask import request
from server.controllers.pricing_controller import PricingController
from server.middleware.auth_middleware import require_role
from server.models.pricing import PricingPolicy
from server import database as db
from server.routes.response_utils import error_response

# Define a namespace for pricing
api = Namespace("Pricing", description="Operations related to product pricing and shipping")

# Define request/response models
product_options_model = api.model("ProductOptions", {
    "group": fields.String(description="Option group name"),
    "options": fields.List(fields.Nested(api.model("Option", {
        "id": fields.Integer(description="Option ID"),
        "name": fields.String(description="Option name")
    })), description="Available options for this group")
})

pricing_request_model = api.model("PricingRequest", {
    "options": fields.List(fields.Integer, description="Selected option IDs"),
    "store_code": fields.Integer(description="Store code (6 for Canada, 9 for US)", default=6),
    "customization": fields.Raw(description="Customization settings that affect price")
})

pricing_response_model = api.model("PricingResponse", {
    "price": fields.Float(description="Product price"),
    "currency": fields.String(description="Currency code"),
    "estimated_ship_date": fields.String(description="Estimated ship date"),
    "pricingBreakdown": fields.Raw(description="Retail pricing breakdown and explanation")
})

shipping_estimate_model = api.model("ShippingEstimateRequest", {
    "items": fields.List(fields.Nested(api.model("CartItem", {
        "productId": fields.Integer(description="Product ID"),
        "options": fields.Raw(description="Selected options")
    })), description="Cart items"),
    "shippingInfo": fields.Nested(api.model("ShippingInfo", {
        "ShipState": fields.String(description="State/Province code"),
        "ShipZip": fields.String(description="ZIP/Postal code"),
        "ShipCountry": fields.String(description="Country code")
    }), description="Shipping destination information")
})

shipping_option_model = api.model("ShippingOption", {
    "carrier_name": fields.String(description="Carrier name"),
    "method_name": fields.String(description="Shipping method name"),
    "price": fields.Float(description="Shipping price"),
    "shipping_days": fields.Integer(description="Delivery days")
})

cart_totals_model = api.model("CartTotals", {
    "subtotal": fields.Float(description="Subtotal amount"),
    "tax": fields.Float(description="Tax amount"),
    "total": fields.Float(description="Total amount"),
    "item_count": fields.Integer(description="Number of items in cart")
})

pricing_policy_model = api.model("PricingPolicy", {
    "vendor_currency": fields.String(description="Vendor currency"),
    "display_currency": fields.String(description="Display currency"),
    "cad_to_usd_rate": fields.Float(description="CAD to USD exchange rate"),
    "exchange_buffer_percent": fields.Float(description="FX protection buffer percentage"),
    "markup_percent": fields.Float(description="Retail markup percentage"),
    "fixed_fee_usd": fields.Float(description="Fixed fee in USD"),
    "minimum_profit_usd": fields.Float(description="Minimum profit floor in USD"),
    "rounding_increment": fields.Float(description="Rounding increment"),
    "customization_file_review_fee_usd": fields.Float(description="File review fee in USD"),
    "customization_design_assist_fee_usd": fields.Float(description="Design assistance fee in USD"),
})


# API Resources
@api.route('/products/<int:product_id>/options')
class ProductOptionsResource(Resource):
    """Resource for getting product options."""
    
    @api.doc('get_product_options')
    @api.param('store_code', 'Store code (6 for Canada, 9 for US)', type='int', default=6)
    @api.response(200, 'Product options retrieved successfully', [product_options_model])
    def get(self, product_id):
        """Get available options for a product."""
        store_code = request.args.get('store_code', 6, type=int)
        
        result = PricingController.get_product_options(product_id, store_code)
        
        if result.status:
            return result.data['options']
        else:
            return error_response(result.error, 400, code='PRICING_OPTIONS_ERROR', category='business_logic')


@api.route('/products/<int:product_id>/price')
class ProductPriceResource(Resource):
    """Resource for calculating product prices."""
    
    @api.doc('calculate_product_price')
    @api.expect(pricing_request_model)
    @api.response(200, 'Pricing calculated successfully', pricing_response_model)
    def post(self, product_id):
        """Calculate price for a product with selected options."""
        data = request.get_json()
        
        if not data:
            return error_response('Request body is required', 400)
        
        options = data.get('options', [])
        store_code = data.get('store_code', 6)
        customization = data.get('customization')
        
        result = PricingController.calculate_price(product_id, options, store_code, customization)
        
        if result.status:
            return result.data
        else:
            return error_response(result.error, 400, code='PRICING_CALCULATION_ERROR', category='business_logic')


@api.route('/policy')
class PricingPolicyResource(Resource):
    """Resource for viewing and updating admin-managed pricing policy."""

    @api.doc('get_pricing_policy')
    @api.response(200, 'Pricing policy fetched successfully', pricing_policy_model)
    @require_role('Admin')
    def get(self):
        policy = PricingPolicy.get_current()
        if not policy:
            policy = PricingPolicy()
            db.session.add(policy)
            db.session.commit()
        return policy.to_dict(), 200

    @api.doc('update_pricing_policy')
    @api.expect(pricing_policy_model)
    @api.response(200, 'Pricing policy updated successfully', pricing_policy_model)
    @require_role('Admin')
    def put(self):
        data = request.get_json(silent=True) or {}
        policy = PricingPolicy.get_current()
        if not policy:
            policy = PricingPolicy()
            db.session.add(policy)

        field_names = [
            'vendor_currency',
            'display_currency',
            'cad_to_usd_rate',
            'exchange_buffer_percent',
            'markup_percent',
            'fixed_fee_usd',
            'minimum_profit_usd',
            'rounding_increment',
            'customization_file_review_fee_usd',
            'customization_design_assist_fee_usd',
        ]

        try:
            for field_name in field_names:
                if field_name in data:
                    setattr(policy, field_name, data[field_name])

            db.session.commit()
            return policy.to_dict(), 200
        except Exception as exc:
            db.session.rollback()
            return error_response(f'Failed to update pricing policy: {str(exc)}', 400, code='PRICING_POLICY_UPDATE_ERROR', category='business_logic')



@api.route('/shipping/estimates')
class ShippingEstimatesResource(Resource):
    """Resource for shipping estimates."""
    
    @api.doc('get_shipping_estimates')
    @api.expect(shipping_estimate_model)
    def post(self):
        """Get shipping estimates for cart items."""
        data = request.get_json()
        
        if not data:
            return error_response('Request body is required', 400)
        
        items = data.get('items', [])
        shipping_info = data.get('shippingInfo', data.get('shipping_info', {}))
        
        if not items or not shipping_info:
            return error_response('items and shippingInfo are required', 400)
        
        result = PricingController.get_shipping_estimates(items, shipping_info)
        
        if result.status:
            return result.data['shipping_options']
        else:
            return error_response(result.error, 400, code='SHIPPING_ESTIMATE_ERROR', category='business_logic')


# Note: The api namespace is exported directly and registered in routes/__init__.py
# This follows the same pattern as print_product_routes.py