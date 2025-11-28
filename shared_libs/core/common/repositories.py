# ======= ایجاد لایه ریپازیتوری برای قوانین انتزاعی تکراری سیستم ======= #
from typing import List, Any, Generic, Dict, Optional, TypeVar

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

T = TypeVar('T', bound=models.Model)

# ======== I Repository ======== #
class IRepository(Generic[T]):
    """ ایجاد لایه انتزاعی برای قوانین سیستم و پایه و اساس آن """
    def __init__(self, model: type[T]):
        self.model = model
    
    def get_by_id(self, pk: Any) -> Optional[T]:
        """ دریافت یک آبجکت با شناسه """
        try:
            return self.model.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return None
    
    def get_by_slug(self, slug: Any) -> Optional[T]:
        """ دریافت یک آبجکت با اسلاگ """
        try:
            return self.model.objects.get(slug=slug)
        except ObjectDoesNotExist:
            return None
    
    def get_all(self) -> List[T]:
        """ دریافت همه آبجکت های موجود """
        return list(self.model.objects.all())
    
    def filter(self, **kwargs) -> List[T]:
        """ دریافت آبجکت های با شرایط مختلف براساس فیلترینگ """
        return list(self.model.objects.filter(**kwargs))
    
    def exists(self, **kwargs) -> bool:
        """ صحت از وجود یک آبجکت در یک مدلاسیون """
        return self.model.objects.filter(**kwargs).exists()
    
    def create(self, data: Dict[str, Any]) -> T:
        """ ایجاد یک آبجکت بااستفاده از فیلدهای مورد نیاز """
        return self.model.objects.create(**data)
    
    def update(self, instance: T, data: Dict[str, Any]) -> T:
        """ ویرایش یک آبجکت براساس فیلدهای مورد نیاز """
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance: T) -> None:
        """ حذف یک آبجکت براساس فیلدهای مورد نیاز """
        instance.delete()
    