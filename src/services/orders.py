from uuid import UUID

import inject
from infrastructure.repositories.orders import OrdersRepository
from models.orders import AddItemResult, OrderStatusEnum
from utils.db import SessionMaker


class OrdersService:
    @inject.autoparams()
    def __init__(
        self,
        orders_repo: OrdersRepository,
        session_maker: SessionMaker,
    ):
        self.repo = orders_repo
        self.session_maker = session_maker

    async def add_item_to_order(self, order_id: UUID, product_id: UUID, quantity: int) -> AddItemResult:
        """Основная бизнес-логика добавления товара в заказ"""
        async with self.session_maker.session() as session:
            order = await self.repo.get_order(order_id, session)
            if not order:
                raise ValueError("Заказ не найден")

            product = await self.repo.get_product(product_id, session)
            if not product:
                raise ValueError("Товар не найден")
            if product.quantity < quantity:
                raise ValueError(f"Недостаточно товара на складе. Доступно: {product.quantity}")

            existing_item = await self.repo.get_order_item(order_id, product_id, session)
            if existing_item:
                await self.repo.update_order_item_quantity(existing_item, quantity, session)
                action = OrderStatusEnum.UPDATED.value
                order_item = existing_item
            else:
                order_item = await self.repo.add_order_item(
                    order_id=order_id, product_id=product_id, quantity=quantity, session=session
                )
                action = OrderStatusEnum.ADDED.value
            new_quantity = product.quantity - quantity
            await self.repo.update_product_stock(product_id, new_quantity, session)

            return AddItemResult(
                action=action,
                order_item={
                    "id": order_item.id,
                    "order_id": order_item.order_id,
                    "product_id": order_item.product_id,
                    "quantity": order_item.quantity,
                    "created_at": order_item.created_at,
                },
                remaining_stock=new_quantity,
            )

    async def get_client_order_totals(self) -> list[dict]:
        """2.1. Сумма товаров по клиентам"""
        async with self.session_maker.session() as session:
            return await self.repo.get_client_order_totals(session)

    async def get_category_child_counts(self) -> list[dict]:
        """2.2. Количество дочерних элементов первого уровня вложенности"""
        async with self.session_maker.session() as session:
            return await self.repo.get_category_child_counts(session)

    async def get_top_products_last_month(self) -> list[dict]:
        """2.3.1. Топ-5 самых покупаемых товаров за последний месяц"""
        async with self.session_maker.session() as session:
            return await self.repo.get_top_products_last_month(session)


def get_service() -> OrdersService:
    return OrdersService()
