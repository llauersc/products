from fastapi import APIRouter, Depends
from models.orders import CategoryChildCountResponse, ClientOrderTotalResponse, TopProductResponse
from services import OrdersService, get_orders_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/client-order-totals", response_model=list[ClientOrderTotalResponse])
async def get_client_order_totals(
    order_service: OrdersService = Depends(get_orders_service)
) -> list[ClientOrderTotalResponse]:
    """
    2.1. Получение информации о сумме товаров заказанных под каждого клиента
    Возвращает: Наименование клиента, сумма
    """
    results = await order_service.get_client_order_totals()
    return [ClientOrderTotalResponse(**item) for item in results]


@router.get("/category-child-counts", response_model=list[CategoryChildCountResponse])
async def get_category_child_counts(
    order_service: OrdersService = Depends(get_orders_service)
) -> list[CategoryChildCountResponse]:
    """
    2.2. Найти количество дочерних элементов первого уровня вложенности для категорий номенклатуры
    """
    results = await order_service.get_category_child_counts()
    return [CategoryChildCountResponse(**item) for item in results]


@router.get("/top-products-last-month", response_model=list[TopProductResponse])
async def get_top_products_last_month(
    order_service: OrdersService = Depends(get_orders_service)
) -> list[TopProductResponse]:
    """
    2.3.1. Топ-5 самых покупаемых товаров за последний месяц
    Возвращает: Наименование товара, Категория 1-го уровня, Общее количество проданных штук
    """
    results = await order_service.get_top_products_last_month()
    return [TopProductResponse(**item) for item in results]
