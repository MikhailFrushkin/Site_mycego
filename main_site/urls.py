from django.urls import path
from .views import MainPage, KnowledgeCategory

app_name = 'main_site'

urlpatterns = [
    path('', MainPage.as_view(), name='main_site'),
    path('category/', KnowledgeCategory.as_view(), name='knowledge_category'),
]
