from django.urls import path

from restaurant import views


urlpatterns = [
    path("api/restaurant/menu/", views.MenuView.as_view(), name="restaurant-menu"),
    path("api/restaurant/products/", views.ProductView.as_view(), name="restaurant-products"),
    path("api/restaurant/products/<name>/", views.ProductDetailView.as_view(), name="restaurant-products-by-name"),
    path("api/restaurant/order/", views.OrderCreateView.as_view(), name="restaurant-order"),
]
