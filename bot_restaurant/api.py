import httpx


class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def get_menu(self):
        result = await self.client.get(f"{self.base_url}/api/restaurant/menu/")
        return result.json()

    async def get_products(self, product_type, date):
        result = await self.client.get(
            f"{self.base_url}/api/restaurant/products/", params={"type": product_type, "date": date}
        )
        return result.json()

    async def get_product(self, name):
        result = await self.client.get(f"{self.base_url}/api/restaurant/products/{name}/")
        return result.json()

    async def create_order(self, data):
        result = await self.client.post(f"{self.base_url}/api/restaurant/order/", json=data)
        return result.json()
