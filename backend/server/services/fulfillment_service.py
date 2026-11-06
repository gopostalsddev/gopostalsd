"""
Fulfillment service: forwards paid GoPostal orders to Sinalite for printing and shipping.

Flow per order:
  1. For each OrderItem, map selected_options (list of IDs) → {group: id_string} using
     cached ProductOption rows.
  2. If the order has artwork, upload each file to R2 and collect public URLs.
  3. Build the Sinalite /order/new payload and call SinaliteAdapter.place_order().
  4. Store the returned Sinalite orderId on Order.sinalite_order_id.
"""

import logging
import time
from typing import Optional
from flask import current_app
from server.config import database as db
from server.models.order import Order
from server.models.pricing import ProductOption

logger = logging.getLogger(__name__)


class FulfillmentService:
    def forward_to_sinalite(self, order: Order) -> bool:
        """
        Forward a paid order to Sinalite. Returns True on success.

        This is designed to be called after payment completes. Any failure is
        logged but does NOT raise, so the payment response is never blocked.
        """
        try:
            sinalite = current_app.extensions.get("sinalite")
            if not sinalite:
                logger.error("Sinalite adapter not in app extensions; cannot forward order %s", order.order_number)
                return False

            artwork_urls = self._upload_artwork(order)
            items = []
            for item in order.items:
                options = self._map_options(item.product_id, item.selected_options)
                files = [{"type": "front", "url": url} for url in artwork_urls]
                items.append({
                    "productId": item.product_id,
                    "options": options,
                    "files": files,
                    "extra": order.order_number,
                })

            addr = order.shipping_address or {}
            bill = order.billing_address or addr
            payload = {
                "items": items,
                "shippingInfo": {
                    "ShipFName": order.customer_first_name or "",
                    "ShipLName": order.customer_last_name or "",
                    "ShipEmail": order.customer_email or "",
                    "ShipAddr": addr.get("street", ""),
                    "ShipAddr2": addr.get("apt", ""),
                    "ShipCity": addr.get("city", ""),
                    "ShipState": addr.get("state", ""),
                    "ShipZip": addr.get("zip_code", ""),
                    "ShipCountry": addr.get("country", "US"),
                    "ShipPhone": order.customer_phone or "",
                    "ShipMethod": order.shipping_method or "UPS Ground",
                },
                "billingInfo": {
                    "BillFName": order.customer_first_name or "",
                    "BillLName": order.customer_last_name or "",
                    "BillEmail": order.customer_email or "",
                    "BillAddr": bill.get("street", ""),
                    "BillAddr2": bill.get("apt", ""),
                    "BillCity": bill.get("city", ""),
                    "BillState": bill.get("state", ""),
                    "BillZip": bill.get("zip_code", ""),
                    "BillCountry": bill.get("country", "US"),
                    "BillPhone": order.customer_phone or "",
                },
                "notes": f"GoPostal order {order.order_number}",
            }

            result = sinalite.place_order(payload)
            if result["success"]:
                order.sinalite_order_id = result["sinalite_order_id"]
                db.session.commit()
                logger.info(
                    "Order %s forwarded to Sinalite (sinalite_order_id=%s)",
                    order.order_number, result["sinalite_order_id"],
                )
                return True

            logger.error(
                "Sinalite rejected order %s: %s", order.order_number, result["error"]
            )
            return False

        except Exception:
            logger.error("Unexpected error forwarding order %s to Sinalite", order.order_number, exc_info=True)
            return False

    def _map_options(self, product_id: int, selected_option_ids) -> dict:
        """
        Convert a list of Sinalite option IDs to the {group: id_string} format
        Sinalite's /order/new endpoint expects.
        """
        if not selected_option_ids:
            return {}

        try:
            ids = [int(x) for x in selected_option_ids]
        except (TypeError, ValueError):
            logger.warning("Could not parse selected_option_ids: %s", selected_option_ids)
            return {}

        rows = ProductOption.query.filter(
            ProductOption.product_id == product_id,
            ProductOption.sinalite_option_id.in_(ids),
        ).all()

        mapped = {row.group: str(row.sinalite_option_id) for row in rows}

        if len(mapped) != len(ids):
            missing = set(ids) - {row.sinalite_option_id for row in rows}
            logger.warning(
                "product_id=%s: %d option(s) not found in cache: %s",
                product_id, len(missing), missing,
            )

        return mapped

    def _upload_artwork(self, order: Order) -> list:
        """
        Upload all OrderArtwork blobs to R2 and return their public URLs.
        Files are uploaded under the prefix artwork/<order_number>/ .
        Returns an empty list if there are no artwork files or the backend is not R2.
        """
        from server.services.file_storage_service import file_storage
        urls = []
        for artwork in order.artwork_files:
            try:
                key = f"artwork_{order.order_number}_{int(time.time())}_{artwork.original_filename}"
                url = file_storage.upload_file(
                    file_data=artwork.file_data,
                    file_name=key,
                    content_type=artwork.mimetype,
                )
                urls.append(url)
                logger.info("Uploaded artwork for order %s → %s", order.order_number, url)
            except Exception:
                logger.error(
                    "Failed to upload artwork id=%s for order %s",
                    artwork.id, order.order_number, exc_info=True,
                )
        return urls


fulfillment_service = FulfillmentService()
