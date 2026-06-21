from flask_restx import Namespace, Resource, reqparse, fields
from werkzeug.datastructures import FileStorage
from server.controllers.print_product_controller import PrintProductController


# Define a namespace for print products
api = Namespace("Print", description="Operations related to print products")

# Define category response model
category_model = api.model("ProductCategory", {
    "id": fields.Integer(description="Category ID"),
    "name": fields.String(description="Category name"),
    "description": fields.String(description="Category description"),
    "image": fields.String(description="Category image URL"),
    "enabled": fields.Boolean(description="Category status"),
    "product_classification_status": fields.Raw(description="Product classification status for this category"),
    "created_at": fields.DateTime(description="Created timestamp"),
    "updated_at": fields.DateTime(description="Updated timestamp"),
})

# Define product type response model
product_type_model = api.model("ProductType", {
    "id": fields.Integer(description="Product Type ID"),
    "name": fields.String(description="Product Type name"),
    "category_id": fields.Integer(description="Category ID this type belongs to"),
    "description": fields.String(description="Product Type description"),
    "image": fields.String(description="Product Type image URL"),
    "created_at": fields.DateTime(description="Created timestamp"),
    "updated_at": fields.DateTime(description="Updated timestamp"),
})

# Define vendor response model
vendor_model = api.model("Vendor", {
    "id": fields.Integer(description="Vendor ID"),
    "name": fields.String(description="Vendor name"),
    "created_at": fields.DateTime(description="Created timestamp"),
    "updated_at": fields.DateTime(description="Updated timestamp"),
})

# Define product response model
product_model = api.model("Product", {
    "id": fields.Integer(description="Product ID"),
    "name": fields.String(description="Product name"),
    "sku": fields.String(description="Stock Keeping Unit"),
    "category_id": fields.Integer(description="Category ID this product belongs to"),
    "type_id": fields.Integer(description="Product Type ID this product belongs to"),
    "description": fields.String(description="Product description"),
    "image": fields.String(description="Product image URL"),
    "vendor_id": fields.Integer(description="Vendor ID this product belongs to"),
    "vendor_product_id": fields.String(description="Vendor's product ID"),
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
    """Resource to fetch all product categories with classification status"""

    @api.doc(description="Fetch all product categories with their classification status")
    @api.marshal_list_with(category_model, code=200)
    def get(self):
        """ Retrieve all product categories with classification status"""
        result = PrintProductController.get_all_product_categories_with_status()

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

@api.route("/products/type/<int:type_id>")
@api.param("type_id", "The product type ID of the products to retrieve")
class PrintProductByTypeResource(Resource):
    """Resource for fetching print products by product type"""

    @api.doc(description="Fetch list of print products by product type")
    @api.marshal_list_with(product_model, code=200)
    @api.response(500, "Server error")
    def get(self, type_id):
        """Retrieve print products by product type"""
        result = PrintProductController.get_products_by_type(type_id)

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
            return {"error": "At least one field (description or image) must be provided"}, 400, {"Content-Type": "application/json"}
        
        result = PrintProductController.update_print_product_category(category_id, description, image)

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 400, {"Content-Type": "application/json"}

# Product Type endpoints
create_product_type_parser = reqparse.RequestParser()
create_product_type_parser.add_argument("name", type=str, location="form", required=True, help="Product type name")
create_product_type_parser.add_argument("category_id", type=int, location="form", required=True, help="Category ID this type belongs to")
create_product_type_parser.add_argument("description", type=str, location="form", required=True, help="Product type description")
create_product_type_parser.add_argument("image", type=FileStorage, location="files", required=False, help="Product type image file")

@api.route("/product-types")
class PrintProductTypesResource(Resource):
    """Resource for fetching all product types"""

    @api.doc(description="Fetch all product types")
    @api.marshal_list_with(product_type_model, code=200)
    @api.response(500, "Server error")
    def get(self):
        """Retrieve all product types"""
        result = PrintProductController.get_all_print_product_types()

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 500

    @api.doc(description="Create a new product type")
    @api.expect(create_product_type_parser)
    @api.response(201, "Product type created successfully")
    @api.response(400, "Bad request")
    @api.response(500, "Server error")
    def post(self):
        """Create a new product type"""
        args = create_product_type_parser.parse_args()
        
        data = {
            "name": args.get("name"),
            "category_id": args.get("category_id"),
            "description": args.get("description"),
            "image": args.get("image")
        }
        
        result = PrintProductController.create_print_product_type(data)

        if result.status:
            return result.data, 201
        else:
            return {"error": result.error}, 400, {"Content-Type": "application/json"}


@api.route("/product-types/ensure-defaults")
class PrintProductTypesEnsureDefaultsResource(Resource):
    """Resource for creating default product types for empty categories"""

    @api.doc(description="Ensure each category has at least one product type")
    @api.response(200, "Default product types ensured")
    @api.response(500, "Server error")
    def post(self):
        """Create default product types for categories that have none"""
        result = PrintProductController.ensure_default_product_types_for_categories()

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 500, {"Content-Type": "application/json"}

@api.route("/product-types/category/<int:category_id>")
@api.param("category_id", "The category ID to filter product types")
class PrintProductTypesByCategoryResource(Resource):
    """Resource for fetching product types by category"""

    @api.doc(description="Fetch product types for a specific category")
    @api.marshal_list_with(product_type_model, code=200)
    @api.response(500, "Server error")
    def get(self, category_id):
        """Retrieve product types for a specific category"""
        result = PrintProductController.get_product_types_by_category(category_id)

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 500

    @api.doc(description="Create a new product type")
    @api.expect(create_product_type_parser)
    @api.response(201, "Product type created successfully")
    @api.response(400, "Bad request")
    @api.response(500, "Server error")
    def post(self):
        """Create a new product type"""
        args = create_product_type_parser.parse_args()
        
        data = {
            "name": args.get("name"),
            "category_id": args.get("category_id"),
            "description": args.get("description"),
            "image": args.get("image")
        }
        
        result = PrintProductController.create_print_product_type(data)

        if result.status:
            return result.data, 201
        else:
            return {"error": result.error}, 400, {"Content-Type": "application/json"}

update_product_type_parser = reqparse.RequestParser()
update_product_type_parser.add_argument("description", type=str, location="form", required=False, help="New description for the product type")
update_product_type_parser.add_argument("image", type=FileStorage, location='files', required=False, help="New image for the product type")

@api.route("/product-types/<int:type_id>/update")
class PrintProductTypeUpdateResource(Resource):
    """Resource for updating a product type's description or image"""

    @api.doc(description="Update the description or image of a product type")
    @api.expect(update_product_type_parser)
    @api.response(200, "Product type updated successfully")
    @api.response(400, "Bad request")
    @api.response(404, "Product type not found")
    @api.response(500, "Server error")
    def put(self, type_id):
        """Update product type description and/or image"""
        args = update_product_type_parser.parse_args()
        description = args.get("description")
        image = args.get("image")

        if not description and not image:
            return {"error": "At least one field (description or image) must be provided"}, 400, {"Content-Type": "application/json"}
        
        result = PrintProductController.update_print_product_type(type_id, description, image)

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 400, {"Content-Type": "application/json"}

@api.route("/product-types/<int:type_id>/delete")
class PrintProductTypeDeleteResource(Resource):
    """Resource for deleting a product type"""

    @api.doc(description="Delete a product type")
    @api.response(200, "Product type deleted successfully")
    @api.response(404, "Product type not found")
    @api.response(400, "Cannot delete: Product type in use")
    @api.response(500, "Server error")
    def delete(self, type_id):
        """Delete a product type"""
        result = PrintProductController.delete_print_product_type(type_id)

        if result.status:
            return result.data, 200
        else:
            if "not found" in result.error.lower():
                return {"error": result.error}, 404, {"Content-Type": "application/json"}
            elif "in use" in result.error.lower():
                return {"error": result.error}, 400, {"Content-Type": "application/json"}
            else:
                return {"error": result.error}, 500, {"Content-Type": "application/json"}

# Product classification endpoints
assign_type_parser = reqparse.RequestParser()
assign_type_parser.add_argument("type_id", type=int, location="json", required=True, help="Product Type ID to assign")

@api.route("/products/<int:product_id>/assign-type")
class PrintProductAssignTypeResource(Resource):
    """Resource for assigning a product to a product type"""

    @api.doc(description="Assign a product to a product type")
    @api.expect(assign_type_parser)
    @api.response(200, "Product assigned successfully")
    @api.response(400, "Bad request")
    @api.response(404, "Product or product type not found")
    @api.response(500, "Server error")
    def put(self, product_id):
        """Assign product to product type"""
        args = assign_type_parser.parse_args()
        type_id = args.get("type_id")
        
        if not type_id:
            return {"error": "type_id is required"}, 400, {"Content-Type": "application/json"}
        
        result = PrintProductController.assign_product_to_type(product_id, type_id)

        if result.status:
            return result.data, 200
        else:
            if "not found" in result.error.lower():
                return {"error": result.error}, 404, {"Content-Type": "application/json"}
            else:
                return {"error": result.error}, 400, {"Content-Type": "application/json"}

@api.route("/products/<int:product_id>/unassign-type")
class PrintProductUnassignTypeResource(Resource):
    """Resource for unassigning a product from its product type"""

    @api.doc(description="Unassign a product from its product type")
    @api.response(200, "Product unassigned successfully")
    @api.response(404, "Product not found")
    @api.response(500, "Server error")
    def put(self, product_id):
        """Unassign product from product type"""
        result = PrintProductController.unassign_product_from_type(product_id)

        if result.status:
            return result.data, 200
        else:
            if "not found" in result.error.lower():
                return {"error": result.error}, 404, {"Content-Type": "application/json"}
            else:
                return {"error": result.error}, 500, {"Content-Type": "application/json"}

@api.route("/products/<int:product_id>/update")
class PrintProductUpdateResource(Resource):
    """Resource for updating a product's description or image"""

    @api.doc(description="Update the description or image of a product")
    @api.expect(update_category_parser)  # Reusing the same parser structure
    @api.response(200, "Product updated successfully")
    @api.response(400, "Bad request")
    @api.response(404, "Product not found")
    @api.response(500, "Server error")
    def put(self, product_id):
        """Update product description and/or image"""
        args = update_category_parser.parse_args()
        description = args.get("description")
        image = args.get("image")

        if not description and not image:
            return {"error": "At least one field (description or image) must be provided"}, 400, {"Content-Type": "application/json"}
        
        result = PrintProductController.update_print_product(product_id, description, image)

        if result.status:
            return result.data, 200
        else:
            if "not found" in result.error.lower():
                return {"error": result.error}, 404, {"Content-Type": "application/json"}
            else:
                return {"error": result.error}, 400, {"Content-Type": "application/json"}

@api.route("/categories/<int:category_id>/classification-status")
class PrintProductCategoryClassificationStatusResource(Resource):
    """Resource for checking if all products in a category are classified"""

    @api.doc(description="Check if all products in a category are classified to product types")
    @api.response(200, "Classification status retrieved successfully")
    @api.response(500, "Server error")
    def get(self, category_id):
        """Check product classification status for a category"""
        result = PrintProductController.are_all_products_classified(category_id)

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 500

@api.route("/vendors")
class PrintProductVendorsResource(Resource):
    """Resource for retrieving all vendors"""

    @api.doc(description="Get all vendors")
    @api.response(200, "Vendors retrieved successfully")
    @api.response(500, "Server error")
    def get(self):
        """Get all vendors"""
        result = PrintProductController.get_all_vendors()

        if result.status:
            return result.data, 200
        else:
            return {"error": result.error}, 500, {"Content-Type": "application/json"}

@api.route("/categories/<int:category_id>/sync-products")
class PrintProductSyncResource(Resource):
    """Resource for syncing products from Sinalite API for a given category"""

    @api.doc(description="Sync products from Sinalite API for a specific category")
    @api.response(200, "Products synced successfully")
    @api.response(404, "Category not found")
    @api.response(500, "Server error")
    def post(self, category_id):
        """Sync products from Sinalite API for a category"""
        result = PrintProductController.sync_print_products(category_id)

        if result.status:
            return result.data, 200
        else:
            if "not found" in result.error.lower():
                return {"error": result.error}, 404, {"Content-Type": "application/json"}
            else:
                return {"error": result.error}, 500, {"Content-Type": "application/json"}