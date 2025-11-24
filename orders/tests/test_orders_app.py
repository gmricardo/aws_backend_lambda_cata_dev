import importlib


def test_app_object_exists():
    mod = importlib.import_module('orders.app')
    assert hasattr(mod, 'app')


def test_orders_routes_present():
    mod = importlib.import_module('orders.app')
    rules = {r.rule for r in mod.app.url_map.iter_rules()}
    assert '/orders' in rules
