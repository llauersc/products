from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from models.orders import AddItemToOrderRequest, AddItemToOrderResponse, OrderItemResponse
from services import OrdersService, get_orders_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/{order_id}/items",
    response_model=AddItemToOrderResponse,
)
async def add_item_to_order(
    order_id: UUID, request: AddItemToOrderRequest, order_service: OrdersService = Depends(get_orders_service)
) -> AddItemToOrderResponse:
    """
    Добавление товара в заказ

    - Принимает ID заказа, ID номенклатуры и количество
    - Если товар уже есть в заказе - увеличивает количество
    - Если товара нет в наличии - возвращает ошибку
    """
    try:
        result = await order_service.add_item_to_order(
            order_id=order_id, product_id=request.product_id, quantity=request.quantity
        )

        return AddItemToOrderResponse(
            message=f"Товар успешно {result.action}",
            order_item=OrderItemResponse(**result.order_item),
            remaining_stock=result.remaining_stock,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
