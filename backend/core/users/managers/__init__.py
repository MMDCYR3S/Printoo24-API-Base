from .users import UserManager, UserQuerySet
from .roles import RoleManager, RoleQuerySet
from .profiles import CustomerProfileManager, CustomerProfileQuerySet
from .address import (
    AddressManager, AddressQuerySet,
    ProvinceManager, ProvinceQuerySet,
    CityManager, CityQuerySet
)