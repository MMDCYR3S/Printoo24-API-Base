from typing import Dict, Any, List
from django.db import transaction
from apps.blog.models import Article, Tutorial, ArticleCategory

# ========== BLOG SERVICE ========== #
class BlogDomainService:
    """ سرویس دامنه برای مدیریت مقالات بلاگ """
    
    @transaction.atomic
    def create_article(self, author, data: Dict[str, Any]) -> Article:
        related_products = data.pop('related_products', [])
        data['author'] = author
        
        article = Article.objects.create(**data)
        
        if related_products:
            article.related_products.set(related_products)
            
        return article

    @transaction.atomic
    def update_article(self, article_id: int, data: Dict[str, Any]) -> Article:
        article = Article.objects.get_detail_by_id(article_id)
        related_products = data.pop('related_products', None)

        for key, value in data.items():
            setattr(article, key, value)
        article.save()

        if related_products is not None:
            article.related_products.set(related_products)

        return article

    def delete_article(self, article_id: int):
        Article.objects.filter(id=article_id).delete()

    @transaction.atomic
    def bulk_update_status(self, article_ids: List[int], status: str) -> int:
        return Article.objects.filter(id__in=article_ids).update(status=status)

    @transaction.atomic
    def bulk_delete(self, article_ids: List[int]) -> int:
        deleted, _ = Article.objects.filter(id__in=article_ids).delete()
        return deleted

# ========== TUTORIAL SERVICE ========== #
class TutorialDomainService:
    """ سرویس دامنه برای مدیریت آموزش‌ها """
    
    @transaction.atomic
    def create_tutorial(self, data: Dict[str, Any]) -> Tutorial:
        related_products = data.pop('related_products', [])
        
        tutorial = Tutorial.objects.create(**data)
        
        if related_products:
            tutorial.related_products.set(related_products)
            
        return tutorial

    @transaction.atomic
    def update_tutorial(self, tutorial_id: int, data: Dict[str, Any]) -> Tutorial:
        tutorial = Tutorial.objects.get_detail_by_id(tutorial_id)
        related_products = data.pop('related_products', None)

        for key, value in data.items():
            setattr(tutorial, key, value)
        tutorial.save()

        if related_products is not None:
            tutorial.related_products.set(related_products)

        return tutorial

    def delete_tutorial(self, tutorial_id: int):
        Tutorial.objects.filter(id=tutorial_id).delete()

    @transaction.atomic
    def bulk_update_status(self, tutorial_ids: List[int], is_active: bool) -> int:
        return Tutorial.objects.filter(id__in=tutorial_ids).update(is_active=is_active)

    @transaction.atomic
    def bulk_delete(self, tutorial_ids: List[int]) -> int:
        deleted, _ = Tutorial.objects.filter(id__in=tutorial_ids).delete()
        return deleted
    
# ========== BLOG CATEGORY DOMAIN SERVICE ========== #
class ArticleCategoryDomainService:
    """ سرویس دامنه برای مدیریت دسته‌بندی‌های بلاگ """
    
    @transaction.atomic
    def create_category(self, data: Dict[str, Any]) -> ArticleCategory:
        # اسلاگ به صورت خودکار در متد save مدل ساخته می‌شود، پس فقط مقادیر پاس داده می‌شود
        return ArticleCategory.objects.create(**data)

    @transaction.atomic
    def update_category(self, category_id: int, data: Dict[str, Any]) -> ArticleCategory:
        category = ArticleCategory.objects.get_detail_by_id(category_id)
        
        for key, value in data.items():
            setattr(category, key, value)
        
        category.save()
        return category

    def delete_category(self, category_id: int):
        ArticleCategory.objects.filter(id=category_id).delete()

    @transaction.atomic
    def bulk_update_status(self, category_ids: List[int], is_active: bool) -> int:
        """ تغییر وضعیت فعال/غیرفعال گروهی """
        return ArticleCategory.objects.filter(id__in=category_ids).update(is_active=is_active)

    @transaction.atomic
    def bulk_delete(self, category_ids: List[int]) -> int:
        """ حذف گروهی دسته‌بندی‌ها """
        # نکته: اگر مقاله‌ای به این دسته متصل باشد و on_delete=PROTECT باشد،
        # دیتابیس ارور ProtectedError می‌دهد که باید در لایه View هندل شود.
        deleted, _ = ArticleCategory.objects.filter(id__in=category_ids).delete()
        return deleted