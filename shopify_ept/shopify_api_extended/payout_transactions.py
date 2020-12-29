from ..shopify.base import ShopifyResource


class Transaction(ShopifyResource):
    _prefix_source = "/shopify_payments/balance/"
