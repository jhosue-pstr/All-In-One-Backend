from app.packages.modulos.blog.module import Module
from app.packages.modulos.blog.models import Category, Post

class BlogModule(Module):
    name = "Blog"
    slug = "blog"
    version = "1.0.0"
    description = "Sistema de blog con posts y categorías"
    icon = "article"
    is_system = True

    def get_models(self):
        from .models import Post, Category
        return [Post, Category]

    def get_schemas(self):
        # ¡CORREGIDO! Usamos los nombres reales que tienes en schemas.py
        from .schemas import PostResponse, CategoryResponse
        return [PostResponse, CategoryResponse]

blog_module = BlogModule()