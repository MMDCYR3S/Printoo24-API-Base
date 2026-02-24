from django.db import models
from django.db.models import Prefetch


# ========== ARTICLE MANAGER ========== #
class ArticleQuerySet(models.QuerySet):
    def get_details(self):
        """ لود کردن روابط برای جلوگیری از مشکل N+1 """
        return self.select_related('author', 'category').prefetch_related('related_products')

    def active_published(self):
        return self.filter(status='published')

class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def get_all_for_dashboard(self):
        return self.get_queryset().get_details().order_by('-created_at')

    def get_detail_by_id(self, pk: int):
        return self.get_queryset().get_details().get(pk=pk)

# ========== TOTURIAL MANAGER ========== #
class TutorialQuerySet(models.QuerySet):
    def get_details(self):
        return self.prefetch_related('related_products')

class TutorialManager(models.Manager):
    def get_queryset(self):
        return TutorialQuerySet(self.model, using=self._db)

    def get_all_for_dashboard(self):
        return self.get_queryset().get_details().order_by('-created_at')

    def get_detail_by_id(self, pk: int):
        return self.get_queryset().get_details().get(pk=pk)
    
# ========== BLOG CATEGORY MANAGER ========== #
class ArticleCategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

class ArticleCategoryManager(models.Manager):
    def get_queryset(self):
        return ArticleCategoryQuerySet(self.model, using=self._db)

    def get_all_for_dashboard(self):
        # برای داشبورد ما تمام دسته‌بندی‌ها (حتی غیرفعال‌ها) را بر اساس جدیدترین می‌خواهیم
        return self.get_queryset().order_by('-id')

    def get_detail_by_id(self, pk: int):
        return self.get_queryset().get(pk=pk)