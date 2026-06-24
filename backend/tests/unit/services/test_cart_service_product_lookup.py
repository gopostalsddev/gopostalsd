from unittest.mock import Mock, patch

from server.services.cart_service import CartService


class TestCartServiceProductLookup:
    def test_get_print_product_uses_string_vendor_product_id(self):
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = Mock()

        with patch('server.services.cart_service.PrintProduct') as mock_print_product:
            mock_print_product.query = mock_query

            result = CartService._get_print_product(122)

        mock_query.filter_by.assert_called_once_with(vendor_product_id='122')
        assert result is not None
