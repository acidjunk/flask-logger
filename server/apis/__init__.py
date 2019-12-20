from flask_restplus import Api

from .v1.categories import api as categories_ns
from .v1.flavors import api as flavors_ns
from .v1.kinds_images import api as kinds_images_ns
from .v1.kinds import api as kinds_ns
from .v1.kinds_to_flavors import api as kinds_to_flavors_ns
from .v1.kinds_to_tags import api as kinds_to_tags_ns
from .v1.orders import api as orders_ns
from .v1.prices import api as prices_ns
from .v1.shops import api as shops_ns
from .v1.shops_to_prices import api as shops_to_prices_ns
from .v1.logs import api as tags_ns
from .v1.users import api as users_ns

api = Api(title="Pricelist API", version="1.0", description="A restful api for the Pricelist")
api.add_namespace(shops_ns, path="/v1/shops")
api.add_namespace(orders_ns, path="/v1/orders")
api.add_namespace(shops_to_prices_ns, path="/v1/shops-to-prices")
api.add_namespace(prices_ns, path="/v1/prices")
api.add_namespace(categories_ns, path="/v1/categories")
api.add_namespace(flavors_ns, path="/v1/flavors")
api.add_namespace(tags_ns, path="/v1/tags")
api.add_namespace(kinds_ns, path="/v1/kinds")
api.add_namespace(kinds_images_ns, path="/v1/kinds-images")
api.add_namespace(kinds_to_tags_ns, path="/v1/kinds-to-tags")
api.add_namespace(kinds_to_flavors_ns, path="/v1/kinds-to-flavors")
api.add_namespace(users_ns, path="/v1/users")
