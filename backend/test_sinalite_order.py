"""
Standalone Sinalite live order test — no Flask app context required.
Reads credentials directly from environment variables.

  sudo GOPOSTAL_IMAGE_TAG=<sha> docker compose -f docker-compose.production.yml \
    run --rm web python test_sinalite_order.py
"""

import os
import time
import requests

BASE_URL       = os.environ["SINALITE_BASE_URL"]
CLIENT_ID      = os.environ["SINALITE_CLIENT_ID"]
CLIENT_SECRET  = os.environ["SINALITE_CLIENT_SECRET"]

print(f"Sinalite URL: {BASE_URL}")

# Authenticate
print("Authenticating ...")
auth_resp = requests.post(
    f"{BASE_URL}/auth/token",
    data={
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type":    "client_credentials",
    },
    timeout=10,
)
if auth_resp.status_code >= 400:
    print(f"✗ Auth failed ({auth_resp.status_code}): {auth_resp.text[:300]}")
    raise SystemExit(1)

token = auth_resp.json().get("access_token")
if not token:
    print(f"✗ No access_token in response: {auth_resp.json()}")
    raise SystemExit(1)

print("✓ Authenticated")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Place a minimal test order
payload = {
    "items": [{
        "productId": 5531,
        "options": {
            "qty":       "105",
            "Turnaround":"18",
            "size":      "583",
            "Bundling":  "88",
            "Coating":   "547",
            "Stock":     "551",
        },
        "files": [],
        "extra": "GOPOSTAL-TEST",
    }],
    "shippingInfo": {
        "ShipFName":   "Test",
        "ShipLName":   "Order",
        "ShipEmail":   "test@uzimaprints.com",
        "ShipAddr":    "123 Test Street",
        "ShipAddr2":   "",
        "ShipCity":    "San Diego",
        "ShipState":   "CA",
        "ShipZip":     "92101",
        "ShipCountry": "US",
        "ShipPhone":   "6195550100",
        "ShipMethod":  "UPS Ground",
    },
    "billingInfo": {
        "BillFName":   "Test",
        "BillLName":   "Order",
        "BillEmail":   "test@uzimaprints.com",
        "BillAddr":    "123 Test Street",
        "BillAddr2":   "",
        "BillCity":    "San Diego",
        "BillState":   "CA",
        "BillZip":     "92101",
        "BillCountry": "US",
        "BillPhone":   "6195550100",
    },
    "notes": "GoPostal connectivity test — safe to cancel",
}

print("Placing test order ...")
order_resp = requests.post(
    f"{BASE_URL}/order/new",
    json=payload,
    headers=headers,
    timeout=15,
)

print(f"HTTP {order_resp.status_code}: {order_resp.text[:500]}")

if order_resp.status_code < 400:
    data = order_resp.json()
    if data.get("status") == "success":
        print(f"\n✓ SUCCESS — Sinalite order ID: {data.get('orderId')}")
        print("Check https://apifrontend.sinaliteuppy.com/ to see it, then cancel it.")
    else:
        print(f"\n✗ Unexpected response: {data}")
else:
    print(f"\n✗ FAILED")
