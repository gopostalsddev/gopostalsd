"""
Repository for pricing-related database operations.
Implements the Repository pattern for clean data access separation.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from sqlalchemy.dialects.postgresql import insert
from server import database as db
from server.models.pricing import (
    ProductOption, ProductPricing, Cart, CartItem, 
    ShippingOption, ProductVariant, StoreCode
)

logger = logging.getLogger(__name__)


class PricingRepository:
    """
    Repository for pricing-related database operations.
    Follows the Repository pattern for clean data access.
    """
    
    def get_cached_pricing(self, product_id: int, store_code: int, option_key: str) -> Optional[Dict]:
        """Retrieve cached pricing data if still valid."""
        try:
            cached = ProductPricing.query.filter_by(
                product_id=product_id,
                store_code=store_code,
                option_key=option_key
            ).first()
            
            if cached and cached.updated_at > datetime.utcnow() - timedelta(hours=1):
                return {
                    'price': str(cached.price),
                    'packageInfo': cached.package_info,
                    'productOptions': cached.product_options
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached pricing: {str(e)}")
            return None
    
    def cache_pricing(self, product_id: int, store_code: int, option_key: str, 
                     pricing_data: Dict, options: List[int]) -> None:
        """Cache pricing data for future use."""
        try:
            # Check if already exists
            existing = ProductPricing.query.filter_by(
                product_id=product_id,
                store_code=store_code,
                option_key=option_key
            ).first()
            
            if existing:
                # Update existing record
                existing.price = pricing_data.get('price', 0)
                existing.package_info = pricing_data.get('packageInfo')
                existing.product_options = pricing_data.get('productOptions')
                existing.updated_at = datetime.utcnow()
            else:
                # Create new record
                new_pricing = ProductPricing(
                    product_id=product_id,
                    store_code=store_code,
                    option_key=option_key,
                    price=pricing_data.get('price', 0),
                    package_info=pricing_data.get('packageInfo'),
                    product_options=pricing_data.get('productOptions')
                )
                db.session.add(new_pricing)
            
            db.session.commit()
            logger.info(f"Cached pricing for product {product_id}")
            
        except Exception as e:
            logger.error(f"Error caching pricing: {str(e)}")
            db.session.rollback()
    
    def get_cached_options(self, product_id: int) -> Optional[List[Dict]]:
        """Retrieve cached product options if available."""
        try:
            cached_options = ProductOption.query.filter_by(
                product_id=product_id
            ).all()
            
            if cached_options:
                return [opt.to_dict() for opt in cached_options]
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached options: {str(e)}")
            return None
    
    def cache_options(self, product_id: int, options: List[Dict]) -> None:
        """Cache product options for future use."""
        try:
            now = datetime.utcnow()

            # Deduplicate payload by option id in case upstream sends repeats.
            deduped_options = {}
            for option in options:
                deduped_options[int(option['id'])] = option

            option_ids = set(deduped_options.keys())

            if option_ids:
                upsert_rows = [
                    {
                        'sinalite_option_id': option_id,
                        'product_id': product_id,
                        'group': option_data['group'],
                        'name': option_data['name'],
                        'updated_at': now,
                    }
                    for option_id, option_data in deduped_options.items()
                ]

                upsert_stmt = insert(ProductOption).values(upsert_rows)
                upsert_stmt = upsert_stmt.on_conflict_do_update(
                    constraint='product_options_sinalite_option_id_key',
                    set_={
                        'product_id': upsert_stmt.excluded.product_id,
                        'group': upsert_stmt.excluded.group,
                        'name': upsert_stmt.excluded.name,
                        'updated_at': upsert_stmt.excluded.updated_at,
                    },
                )
                db.session.execute(upsert_stmt)

                # Remove stale options cached for this product only.
                ProductOption.query.filter(
                    ProductOption.product_id == product_id,
                    ~ProductOption.sinalite_option_id.in_(option_ids)
                ).delete(synchronize_session=False)
            else:
                ProductOption.query.filter_by(product_id=product_id).delete(synchronize_session=False)
            
            db.session.commit()
            logger.info(f"Cached {len(deduped_options)} options for product {product_id}")
            
        except Exception as e:
            logger.error(f"Error caching options: {str(e)}")
            db.session.rollback()
    
    def get_cached_variants(self, product_id: int, offset: int) -> Optional[List[Dict]]:
        """Retrieve cached product variants if available."""
        try:
            cached_variants = ProductVariant.query.filter_by(
                product_id=product_id
            ).offset(offset).limit(1000).all()
            
            if cached_variants:
                return [variant.to_dict() for variant in cached_variants]
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached variants: {str(e)}")
            return None
    
    def cache_variants(self, product_id: int, variants: List[Dict]) -> None:
        """Cache product variants for future use."""
        try:
            # Clear existing variants for this product
            ProductVariant.query.filter_by(product_id=product_id).delete()
            
            # Add new variants
            for variant in variants:
                new_variant = ProductVariant(
                    product_id=product_id,
                    variant_key=variant['key'],
                    price=variant['price']
                )
                db.session.add(new_variant)
            
            db.session.commit()
            logger.info(f"Cached {len(variants)} variants for product {product_id}")
            
        except Exception as e:
            logger.error(f"Error caching variants: {str(e)}")
            db.session.rollback()


