from apps.blog.services import BlogDomainService, TutorialDomainService, ArticleCategoryDomainService
from apps.blog.models import Article, Tutorial, ArticleCategory

# ========== BLOG SERVICE ========== #
class DashboardBlogService:
    def __init__(self):
        self._domain_service = BlogDomainService()

    def get_all_articles(self):
        return Article.objects.get_all_for_dashboard()

    def get_article_detail(self, article_id: int):
        return Article.objects.get_detail_by_id(article_id)

    def create_article(self, user, data: dict):
        return self._domain_service.create_article(author=user, data=data)

    def update_article(self, article_id: int, data: dict):
        return self._domain_service.update_article(article_id, data)

    def delete_article(self, article_id: int):
        self._domain_service.delete_article(article_id)

    def bulk_update_status(self, article_ids: list, status: str):
        return self._domain_service.bulk_update_status(article_ids, status)

    def bulk_delete(self, article_ids: list):
        return self._domain_service.bulk_delete(article_ids)

# ========== TUTORIAL SERVICE ========== #
class DashboardTutorialService:
    def __init__(self):
        self._domain_service = TutorialDomainService()

    def get_all_tutorials(self):
        return Tutorial.objects.get_all_for_dashboard()

    def get_tutorial_detail(self, tutorial_id: int):
        return Tutorial.objects.get_detail_by_id(tutorial_id)

    def create_tutorial(self, data: dict):
        return self._domain_service.create_tutorial(data)

    def update_tutorial(self, tutorial_id: int, data: dict):
        return self._domain_service.update_tutorial(tutorial_id, data)

    def delete_tutorial(self, tutorial_id: int):
        self._domain_service.delete_tutorial(tutorial_id)

    def bulk_update_status(self, tutorial_ids: list, is_active: bool):
        return self._domain_service.bulk_update_status(tutorial_ids, is_active)

    def bulk_delete(self, tutorial_ids: list):
        return self._domain_service.bulk_delete(tutorial_ids)
    
# ========== DASHBOARD BLOG CATEGORY APP SERVICE ========== #
class DashboardArticleCategoryService:
    """ سرویس واسط اپلیکیشن داشبورد برای دسته‌بندی مقالات """
    
    def __init__(self):
        self._domain_service = ArticleCategoryDomainService()

    def get_all_categories(self):
        return ArticleCategory.objects.get_all_for_dashboard()

    def get_category_detail(self, category_id: int):
        return ArticleCategory.objects.get_detail_by_id(category_id)

    def create_category(self, data: dict):
        return self._domain_service.create_category(data)

    def update_category(self, category_id: int, data: dict):
        return self._domain_service.update_category(category_id, data)

    def delete_category(self, category_id: int):
        self._domain_service.delete_category(category_id)

    def bulk_update_status(self, category_ids: list, is_active: bool):
        return self._domain_service.bulk_update_status(category_ids, is_active)

    def bulk_delete(self, category_ids: list):
        return self._domain_service.bulk_delete(category_ids)
