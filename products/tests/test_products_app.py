import importlib


def test_app_object_exists():
    mod = importlib.import_module('products.app')
    assert hasattr(mod, 'app')


def test_products_routes_present():
    mod = importlib.import_module('products.app')
    rules = {r.rule for r in mod.app.url_map.iter_rules()}
    assert '/products' in rules
