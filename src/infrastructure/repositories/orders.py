import uuid
from datetime import datetime
from uuid import UUID

import inject
from models.orders import OrderDB, OrderItemDB, ProductDB
from sqlalchemy import and_, func, insert, literal, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from utils.db import SessionMaker

from infrastructure.repositories.db_models import categories, clients, order_items, orders, products


class OrdersRepository:
    @inject.params(session_maker=SessionMaker)
    def __init__(self, session_maker: SessionMaker):
        self.session_maker = session_maker

    async def get_order(self, order_id: UUID, session: AsyncSession) -> OrderDB | None:
        query = select(orders).where(orders.c.id == order_id)
        result = await session.execute(query)
        if row := result.fetchone():
            return OrderDB.model_validate(row, from_attributes=True)
        return None

    async def get_order_item(self, order_id: UUID, product_id: UUID, session: AsyncSession) -> OrderItemDB | None:
        query = select(order_items).where(
            and_(order_items.c.order_id == order_id, order_items.c.product_id == product_id)
        )
        result = await session.execute(query)
        if row := result.fetchone():
            return OrderItemDB.model_validate(row, from_attributes=True)
        return None

    async def add_order_item(
        self, order_id: UUID, product_id: UUID, quantity: int, session: AsyncSession
    ) -> OrderItemDB:
        order_item = {
            "id": uuid.uuid4(),
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "created_at": datetime.now(),
        }
        query = insert(order_items).values(order_item).returning(order_items)
        await session.execute(query)
        return OrderItemDB(**order_item)

    async def update_order_item_quantity(self, order_item: OrderItemDB, quantity: int, session: AsyncSession) -> None:
        order_item.quantity += quantity
        await session.commit()

    async def get_product(self, product_id: UUID, session: AsyncSession) -> ProductDB | None:
        query = select(products).where(products.c.id == product_id)
        result = await session.execute(query)
        row = result.fetchone()
        return ProductDB.model_validate(row, from_attributes=True)

    async def update_product_stock(self, product_id: UUID, new_quantity: int, session: AsyncSession) -> None:
        query = update(products).where(products.c.id == product_id).values(quantity=new_quantity)
        await session.execute(query)
        await session.commit()

    async def get_client_order_totals(self, session: AsyncSession) -> list[dict]:
        """2.1. Сумма товаров по клиентам"""
        query = (
            select(
                clients.c.name.label("client_name"),
                func.sum(order_items.c.quantity * products.c.price).label("total_amount"),
            )
            .select_from(clients)
            .join(orders, orders.c.client_id == clients.c.id)
            .join(order_items, order_items.c.order_id == orders.c.id)
            .join(products, products.c.id == order_items.c.product_id)
            .group_by(clients.c.id, clients.c.name)
        )

        result = await session.execute(query)
        rows = result.all()
        return [
            {"client_name": row.client_name, "total_amount": float(row.total_amount) if row.total_amount else 0.0}
            for row in rows
        ]

    async def get_category_child_counts(self, session: AsyncSession) -> list[dict]:
        """2.2. Количество дочерних элементов первого уровня"""
        parent = aliased(categories)
        child = aliased(categories)

        subquery = (
            select(child.c.parent_id, func.count(child.c.id).label("child_count"))
            .select_from(child)
            .where(child.c.parent_id.is_not(None))
            .group_by(child.c.parent_id)
            .subquery()
        )

        query = (
            select(parent.c.name.label("category_name"), func.coalesce(subquery.c.child_count, 0).label("child_count"))
            .select_from(parent)
            .outerjoin(subquery, parent.c.id == subquery.c.parent_id)
        )

        result = await session.execute(query)
        rows = result.all()
        return [{"category_name": row.category_name, "child_count": row.child_count} for row in rows]

    async def get_top_products_last_month(self, session: AsyncSession) -> list[dict]:
        """2.3.1. Топ-5 самых покупаемых товаров за последний месяц"""
        # Рекурсивный CTE для нахождения корневых категорий
        category_hierarchy = (
            select(
                categories.c.id,
                categories.c.parent_id,
                categories.c.name,
                categories.c.name.label("root_name"),
                literal(0).label("level"),
            )
            .where(categories.c.parent_id.is_(None))
            .cte(name="category_hierarchy", recursive=True)
        )

        recursive_part = (
            select(
                categories.c.id,
                categories.c.parent_id,
                categories.c.name,
                category_hierarchy.c.root_name,  # наследуем root_name от родителя
                (category_hierarchy.c.level + 1).label("level"),
            )
            .select_from(categories)
            .join(category_hierarchy, categories.c.parent_id == category_hierarchy.c.id)
        )

        category_hierarchy = category_hierarchy.union_all(recursive_part)

        query = (
            select(
                products.c.name.label("product_name"),
                category_hierarchy.c.root_name.label("top_level_category"),
                func.sum(order_items.c.quantity).label("total_sold"),
            )
            .select_from(products)
            .join(order_items, order_items.c.product_id == products.c.id)
            .join(orders, orders.c.id == order_items.c.order_id)
            .outerjoin(category_hierarchy, products.c.category_id == category_hierarchy.c.id)
            .group_by(products.c.id, products.c.name, category_hierarchy.c.root_name)
            .order_by(func.sum(order_items.c.quantity).desc())
            .limit(5)
        )

        result = await session.execute(query)
        rows = result.all()
        return [
            {
                "product_name": row.product_name,
                "top_level_category": row.top_level_category,
                "total_sold": row.total_sold or 0,
            }
            for row in rows
        ]
