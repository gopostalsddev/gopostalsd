"""
One-time migration: download category images from Supabase, upload to R2,
update the database URLs in place.

Run inside the Docker Compose network:
  sudo GOPOSTAL_IMAGE_TAG=<sha> docker compose -f docker-compose.production.yml \
    run --rm web python migrate_images_to_r2.py
"""

import os
import time
import requests
import boto3
from botocore.config import Config
from server import create_server

app = create_server()

with app.app_context():
    from server import database as db

    # R2 client
    r2 = boto3.client(
        "s3",
        endpoint_url=app.config["R2_ENDPOINT_URL"],
        aws_access_key_id=app.config["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=app.config["R2_SECRET_ACCESS_KEY"],
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )
    bucket = app.config["R2_BUCKET"]
    public_url = app.config["R2_PUBLIC_URL"].rstrip("/")

    rows = db.session.execute(
        db.text("SELECT id, image FROM print_product_categories WHERE image LIKE :pat"),
        {"pat": "%supabase%"},
    ).fetchall()

    print(f"Found {len(rows)} categories to migrate")
    ok = 0
    fail = 0

    for row_id, old_url in rows:
        try:
            resp = requests.get(old_url, timeout=15)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0]
            ext = old_url.rsplit(".", 1)[-1].split("?")[0] or "jpg"
            key = f"{int(time.time())}_{row_id}.{ext}"
            r2.put_object(Bucket=bucket, Key=key, Body=resp.content, ContentType=content_type)
            new_url = f"{public_url}/{key}"
            db.session.execute(
                db.text("UPDATE print_product_categories SET image = :new WHERE id = :id"),
                {"new": new_url, "id": row_id},
            )
            db.session.commit()
            print(f"  [{row_id}] OK -> {new_url}")
            ok += 1
        except Exception as e:
            db.session.rollback()
            print(f"  [{row_id}] FAILED: {e}")
            fail += 1

    print(f"\nDone: {ok} migrated, {fail} failed")
