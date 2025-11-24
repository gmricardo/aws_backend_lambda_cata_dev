import importlib


def test_app_object_exists():
    mod = importlib.import_module('auth.app')
    assert hasattr(mod, 'app')


def test_auth_routes_present():
    mod = importlib.import_module('auth.app')
    rules = {r.rule for r in mod.app.url_map.iter_rules()}
    assert '/register' in rules
    assert '/login' in rules
