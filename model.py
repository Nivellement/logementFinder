# model.py
from dataclasses import dataclass
from typing import Callable, List, Optional
import lbc

@dataclass
class Parameters:
    text: Optional[str] = None
    locations: Optional[List[lbc.City]] = None
    category: Optional[str] = None
    real_estate_type: Optional[List[str]] = None
    square: Optional[List[int]] = None
    price: Optional[List[int]] = None

@dataclass
class Search:
    name: str
    parameters: Parameters
    handler: Callable[[lbc.Ad, str], None]
    proxy: Optional[lbc.Proxy] = None