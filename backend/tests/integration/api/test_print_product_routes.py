"""Integration tests for print product route error status semantics."""

import json
from unittest.mock import patch

from server.controllers.helpers import Result


class TestPrintProductRoutes:
    def test_get_enabled_products_by_category_not_found_returns_404(self, client):
        with patch(
            "server.routes.print_product_routes.PrintProductController.get_enabled_products_by_category"
        ) as mock_controller:
            mock_controller.return_value = Result(
                status=False,
                error="Print product category not found",
            )

            response = client.get("/api/print/products/9999")

            assert response.status_code == 404
            payload = json.loads(response.data)
            assert payload["error"]["message"] == "Print product category not found"
            assert payload["error"]["code"] == "PRODUCTS_BY_CATEGORY_ERROR"
            assert payload["error"]["category"] == "business_logic"

    def test_get_all_products_by_category_not_found_returns_404(self, client):
        with patch(
            "server.routes.print_product_routes.PrintProductController.get_all_products_by_category"
        ) as mock_controller:
            mock_controller.return_value = Result(
                status=False,
                error="Print product category not found",
            )

            response = client.get("/api/print/products/9999/all")

            assert response.status_code == 404
            payload = json.loads(response.data)
            assert payload["error"]["message"] == "Print product category not found"
            assert payload["error"]["code"] == "ALL_PRODUCTS_BY_CATEGORY_ERROR"
            assert payload["error"]["category"] == "business_logic"

    def test_get_products_by_type_not_found_returns_404(self, client):
        with patch(
            "server.routes.print_product_routes.PrintProductController.get_products_by_type"
        ) as mock_controller:
            mock_controller.return_value = Result(
                status=False,
                error="Print product type not found",
            )

            response = client.get("/api/print/products/type/9999")

            assert response.status_code == 404
            payload = json.loads(response.data)
            assert payload["error"]["message"] == "Print product type not found"
            assert payload["error"]["code"] == "PRODUCTS_BY_TYPE_ERROR"
            assert payload["error"]["category"] == "business_logic"
