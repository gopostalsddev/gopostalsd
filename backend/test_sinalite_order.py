"""
One-shot test: place a minimal order on the live Sinalite API without going
through Square or charging any card. Run inside the Docker Compose network:

  sudo GOPOSTAL_IMAGE_TAG=16c0845 docker compose -f docker-compose.production.yml \
    run --rm web python test_sinalite_order.py

The script will print the Sinalite orderId on success. Check it in the
Sinalite live dashboard at https://apifrontend.sinaliteuppy.com/
"""

from server import create_server

app = create_server()

with app.app_context():
    from server.models.pricing import ProductOption

    # Use a product that was already seen working in the logs
    PRODUCT_ID = 5531

    # Look up cached options for this product to build a valid options dict
    cached = ProductOption.query.filter_by(product_id=PRODUCT_ID).all()
    if not cached:
        print(f"ERROR: No cached options for product {PRODUCT_ID}.")
        print("Browse that product on the site first so options get cached, then re-run.")
        raise SystemExit(1)

    options = {row.group: str(row.sinalite_option_id) for row in cached}
    print(f"Using product {PRODUCT_ID} with options: {options}")

    payload = {
        "items": [{
            "productId": PRODUCT_ID,
            "options": options,
            "files": [],          # no artwork for the test
            "extra": "GOPOSTAL-TEST",
        }],
        "shippingInfo": {
            "ShipFName": "Test",
            "ShipLName": "Order",
            "ShipEmail": "test@uzimaprints.com",
            "ShipAddr": "123 Test Street",
            "ShipAddr2": "",
            "ShipCity": "San Diego",
            "ShipState": "CA",
            "ShipZip": "92101",
            "ShipCountry": "US",
            "ShipPhone": "6195550100",
            "ShipMethod": "UPS Ground",
        },
        "billingInfo": {
            "BillFName": "Test",
            "BillLName": "Order",
            "BillEmail": "test@uzimaprints.com",
            "BillAddr": "123 Test Street",
            "BillAddr2": "",
            "BillCity": "San Diego",
            "BillState": "CA",
            "BillZip": "92101",
            "BillCountry": "US",
            "BillPhone": "6195550100",
        },
        "notes": "GoPostal connectivity test — safe to cancel",
    }

    sinalite = app.extensions["sinalite"]
    print("Authenticating with Sinalite live API ...")
    result = sinalite.place_order(payload)

    if result["success"]:
        print(f"\n✓ SUCCESS — Sinalite order ID: {result['sinalite_order_id']}")
        print("Check https://apifrontend.sinaliteuppy.com/ to see it, then cancel it.")
    else:
        print(f"\n✗ FAILED — {result['error']}")
