from ..shopify.base import ShopifyResource


class Payout(ShopifyResource):
    _prefix_source = "/shopify_payments/"
