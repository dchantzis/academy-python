"""Python types, comprehensions, functions and properties."""
from dataclasses import dataclass

@dataclass(frozen=True)
class LineItem:
    sku: str
    price_minor: int
    quantity: int

    @property
    def total_minor(self) -> int:
        return self.price_minor * self.quantity

def order_total(items: list[LineItem]) -> int:
    return sum(item.total_minor for item in items)

if __name__ == "__main__":
    items = [LineItem("PRINT-A3", 2500, 2), LineItem("CARD", 300, 1)]
    print("SKUs:", [item.sku for item in items])
    print("Order total (minor units):", order_total(items))
