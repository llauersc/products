import sqlalchemy as sa
from sqlalchemy import ForeignKey, func

metadata = sa.MetaData()

categories = sa.Table(
    "categories",
    metadata,
    sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), primary_key=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("parent_id", sa.UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True),
    sa.Column("created_at", sa.DateTime, server_default=func.now(), nullable=False),
)

products = sa.Table(
    "products",
    metadata,
    sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), primary_key=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("quantity", sa.Integer, nullable=False, default=0),
    sa.Column("price", sa.Numeric(10, 2), nullable=False),
    sa.Column("category_id", sa.UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True),
    sa.Column("created_at", sa.DateTime, server_default=func.now(), nullable=False),
)

clients = sa.Table(
    "clients",
    metadata,
    sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), primary_key=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("address", sa.Text, nullable=True),
    sa.Column("created_at", sa.DateTime, server_default=func.now(), nullable=False),
)

orders = sa.Table(
    "orders",
    metadata,
    sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), primary_key=True),
    sa.Column("client_id", sa.UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False),
    sa.Column("status", sa.String(50), nullable=False, default="active"),
    sa.Column("created_at", sa.DateTime, server_default=func.now(), nullable=False),
    sa.Column("updated_at", sa.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False),
)

order_items = sa.Table(
    "order_items",
    metadata,
    sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), primary_key=True),
    sa.Column("order_id", sa.UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False),
    sa.Column("product_id", sa.UUID(as_uuid=True), ForeignKey("products.id"), nullable=False),
    sa.Column("quantity", sa.Integer, nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=func.now(), nullable=False),
    sa.UniqueConstraint("order_id", "product_id", name="uq_order_product"),
)
