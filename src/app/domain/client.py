from dataclasses import dataclass
from typing import Optional


@dataclass
class Client:
    name: Optional[str] = None
    email: Optional[str] = None
    sku_number: Optional[str] = None
