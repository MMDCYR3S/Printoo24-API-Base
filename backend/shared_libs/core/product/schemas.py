from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class CategoryAssignment:
    category_id: int
    is_primary: bool = False
    priority: int = 3
    order: int = 0