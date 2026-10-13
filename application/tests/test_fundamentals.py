import importlib.util
from pathlib import Path

def load_example():
    file = Path(__file__).resolve().parents[1] / "lessons/01-python-modules-and-types/examples/fundamentals.py"
    spec = importlib.util.spec_from_file_location("fundamentals", file)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_order_total():
    module = load_example()
    assert module.order_total([module.LineItem("A", 100, 2), module.LineItem("B", 50, 1)]) == 250
