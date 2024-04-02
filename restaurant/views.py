import datetime

from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from restaurant.models import Menu, Order, Product
from restaurant.serializers import MenuSerializer, OrderRequestSerializer, ProductRequestSerializer, ProductSerializer


class MenuView(APIView):
    def get(self, request, *args, **kwargs):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        return Response(MenuSerializer(Menu.objects.filter(date=tomorrow), many=True).data)


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="type", description="Product type", type=str, required=True, enum=Product.PRODUCT_TYPES
            ),
            OpenApiParameter(name="date", description="Date", type=str, required=True),
        ]
    )
)
class ProductView(APIView):
    def get(self, request, *args, **kwargs):
        data = ProductRequestSerializer(data=self.request.query_params)
        data.is_valid(raise_exception=True)
        queryset = Product.objects.filter(
            product_type=data.validated_data["type"], menus__date=data.validated_data["date"]
        )
        if not queryset.exists():
            return Response([], status=404)
        result = ProductSerializer(queryset, many=True)
        return Response(result.data)


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects
    lookup_url_kwarg = "name"
    lookup_field = "name"
    serializer_class = ProductSerializer


class OrderCreateView(CreateAPIView):
    serializer_class = OrderRequestSerializer
    queryset = Order.objects.all()
