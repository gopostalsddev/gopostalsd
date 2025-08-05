from flask_restx import Namespace, Resource, reqparse, fields
from werkzeug.datastructures import FileStorage
from server.controllers.print_product_controller import PrintProductController


# Define a namespace for print products
api = Namespace("Print", description="Operations related to print products")

# Define a product response model
product_model = api.model("Product", {
    "id": fields.Integer(description="Product ID"),
    "sku": fields.String(description="Stock Keeping Unit (SKU)"),
    "name": fields.String(description="Product name"),
    "category": fields.String(description="Product category"),
    "enabled": fields.Integer(description="Product availability status"),
})

# Define category response model
category_model = api.model("ProductCategory", {
    "id": fields.Integer(description="Category ID"),
    "name": fields.String(description="Category name"),
    "description": fields.String(description="Category description"),
    "image": fields.String(description="Category image URL"),
    "enabled": fields.Boolean(description="Category status"),
    "created_at": fields.DateTime(description="Created timestamp"),
    "updated_at": fields.DateTime(description="Updated timestamp"),
})


@api.route("/products")
class PrintProductResource(Resource):
    """Ressource for fetching print products"""

    @api.doc(description="Fetch list of available print products")
    @api.marshal_list_with(product_model, code=200)
    @api.response(500, "Server error")
    def get(self):
        """Retrieve available print products"""
        result = PrintProductController.get_all_products()

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 500
        
@api.route("/categories/all")
class PrintProductCategoriesResource(Resource):
    """Ressource to fetch all product categories"""

    @api.doc(description="Fetch all product categories")
    @api.marshal_list_with(category_model, code=200)
    def get(self):
        """ Retrieve all product categories"""
        result = PrintProductController.get_all_product_categories()

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 500

@api.route("/categories")
class PrintProductCategoriesEnabledResource(Resource):
    """Resource of fetching only enabled categories"""
    
    @api.doc(description="Fetches only enabled product categories")
    @api.marshal_list_with(category_model, code=200)
    def get(self):
        """Retrieves enabled product categories"""
      
        result = PrintProductController.get_enabled_product_categories()
        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 500

@api.route("/categories/<int:category_id>/status")
class PrintProductCategoryStatusResource(Resource):
    """Enabled and disabling category"""

    @api.doc(description="Enable or disable a product category")
    @api.param("enabled", "Enable (true) or disable (false) the category", type=bool, required=True)
    def put(self, category_id):
        """Updates category status"""
        from flask import request
    
        # Get enabled from query params instead of JSON body
        enabled = request.args.get("enabled", type=lambda arg: arg.lower() == "true")
        result = PrintProductController.update_print_product_category_status(category_id, enabled)

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 500

@api.route("/categories/sync")
class PrintProductCategorySyncResource(Resource):
    """Resource for syncing categories from Sinalite API"""

    @api.doc(description="Manually sync new categories from Sinalite API")
    def post(self):
        """Sync new categories"""
        result = PrintProductController.sync_print_product_categories()
        
        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 500

@api.route("/products/<int:category_id>")
@api.param("category_id", "The category ID of the products to retrieve")
class PrintProductByCategoryEnabledResource(Resource):
    """Resource for fetching print products by category"""

    @api.doc(description="Fetch list of print products listed by category")
    @api.marshal_list_with(product_model, code=200)
    @api.response(500, "Server error")
    def get(self, category_id):
        """Retrieve print products by category"""
        result = PrintProductController.get_enabled_products_by_category(category_id)

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 200

@api.route("/products/<int:category_id>/all")
@api.param("category_id", "The category ID of the products to retrieve")
class PrintProductByCategoryAllResource(Resource):
    """Resource for fetching print products by category"""

    @api.doc(description="Fetch list of print products listed by category")
    @api.marshal_list_with(product_model, code=200)
    @api.response(500, "Server error")
    def get(self, category_id):
        """Retrieve print products by category"""

        result = PrintProductController.get_all_products_by_category(category_id)
       
        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 200

update_category_parser = reqparse.RequestParser()
update_category_parser.add_argument("description", type=str, location="form", required=False, help="New description for the category")
update_category_parser.add_argument("image", type=FileStorage, location='files', required=False, help="New image for the category")

@api.route("/categories/<int:category_id>/update")
class PrintProductCategoryUpdateResource(Resource):
    """Resource for updating a print product category's image or description"""

    @api.doc(description="Update the description or image of a product category")
    @api.expect(update_category_parser)
    def put(self, category_id):
        """Update category image and/or description"""
        args = update_category_parser.parse_args()
        description = args.get("description")
        image = args.get("image")

        if not description and not image:
            return {"error": "At least one field (description or image) must be provided"}, 400
        
        result = PrintProductController.update_print_product_category(category_id, description, image)

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 400