"""Response contracts. Validating responses against these models doubles as schema testing."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class AuthResponse(ApiModel):
    id: int
    username: str
    email: str
    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")


class User(ApiModel):
    id: int
    username: str
    email: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")


class Product(ApiModel):
    id: int
    title: str
    price: float
    category: str | None = None
    description: str | None = None
    brand: str | None = None
    stock: int | None = None
    rating: float | None = None


class ProductList(ApiModel):
    products: list[Product]
    total: int
    skip: int
    limit: int


class DeletedProduct(Product):
    is_deleted: bool = Field(alias="isDeleted")
    deleted_on: str = Field(alias="deletedOn")


class ErrorResponse(ApiModel):
    message: str
