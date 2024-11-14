from typing import Any

from sqladmin import ModelView
from starlette.requests import Request

from db import Product, Categorie, Order, Cart, User


class CategoryAdmin(ModelView, model=Categorie):
    column_list = ['id', 'name']
    column_details_list = ['id', 'name']
    form_rules = [
        "name",
        "parent"
    ]
    can_export = False
    name_plural = 'Kategoriyalar'
    name = 'Kategoriya'


class ProductAdmin(ModelView, model=Product):
    # column_list = [Product.id, Product.name, Product.photo]
    column_labels = dict(id="ID", title="Nomi", price="Narxi")
    column_formatters = {Product.price: lambda obj, a: f"${obj.price}"}
    column_list = ['id', 'title', 'price']
    column_searchable_list = [Product.title]
    # column_details_exclude_list = ['created_at', 'updated_at']
    # form_excluded_columns = ['created_at', 'updated_at', 'slug', 'owner']
    form_columns = [
        'category',
        'title',
        'photo',
        'description',
        'price',
        'type',
        'category_id'
    ]
    name_plural = 'Mahsulotlar'
    name = 'Mahsulot'

    # async def insert_model(self, request: Request, data: dict) -> Any:
    #     data['owner_id'] = request.session['user']['id']
    #     return await super().insert_model(request, data)
