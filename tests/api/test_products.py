import allure
import pytest

from framework.api import ProductsClient
from framework.api.models import DeletedProduct, Product, ProductList
from framework.utils import data_factory


@allure.epic("Platform API")
@allure.feature("Products")
class TestProducts:
    @pytest.mark.smoke
    @allure.title("Product {product_id} can be fetched by id")
    @pytest.mark.parametrize("product_id", [1, 2, 30])
    def test_get_product(self, products_client: ProductsClient, product_id: int) -> None:
        response = products_client.get_by_id(product_id)

        assert response.status == 200
        product = Product.model_validate(response.json())
        assert product.id == product_id
        assert product.price > 0

    @pytest.mark.regression
    @allure.title("Unknown product returns 404")
    def test_get_unknown_product(self, products_client: ProductsClient) -> None:
        response = products_client.get_by_id(999_999)

        assert response.status == 404

    @pytest.mark.regression
    @allure.title("Product list supports pagination (limit={limit}, skip={skip})")
    @pytest.mark.parametrize(("limit", "skip"), [(5, 0), (10, 10), (1, 50)])
    def test_pagination(self, products_client: ProductsClient, limit: int, skip: int) -> None:
        response = products_client.list_products(limit=limit, skip=skip)

        assert response.status == 200
        page = ProductList.model_validate(response.json())
        assert len(page.products) == limit
        assert (page.limit, page.skip) == (limit, skip)
        assert page.products[0].id == skip + 1

    @pytest.mark.regression
    @allure.title("Search returns only matching products")
    def test_search(self, products_client: ProductsClient) -> None:
        query = "phone"

        response = products_client.search(query)

        assert response.status == 200
        results = ProductList.model_validate(response.json()).products
        assert results, f"No products found for '{query}'"
        for product in results:
            haystack = f"{product.title} {product.description or ''}".lower()
            assert query in haystack, f"'{product.title}' does not match '{query}'"

    @pytest.mark.smoke
    @allure.title("Product can be created")
    def test_create_product(self, products_client: ProductsClient) -> None:
        payload = data_factory.new_product_payload()

        response = products_client.create(payload)

        assert response.status == 201
        created = Product.model_validate(response.json())
        assert created.id > 0
        assert (created.title, created.price) == (payload["title"], payload["price"])

    @pytest.mark.regression
    @allure.title("Product can be updated")
    def test_update_product(self, products_client: ProductsClient) -> None:
        new_title = data_factory.new_product_payload()["title"]

        response = products_client.update(1, {"title": new_title})

        assert response.status == 200
        updated = Product.model_validate(response.json())
        assert (updated.id, updated.title) == (1, new_title)

    @pytest.mark.regression
    @allure.title("Product can be deleted")
    def test_delete_product(self, products_client: ProductsClient) -> None:
        response = products_client.remove(1)

        assert response.status == 200
        deleted = DeletedProduct.model_validate(response.json())
        assert deleted.id == 1
        assert deleted.is_deleted is True
