1. Спроектирована схема БД
Реляционная модель данных с сущностями:

Номенклатура (products) - наименование, количество, цена

Каталог номенклатуры (categories) - дерево категорий с неограниченной вложенностью

Клиенты (clients) - наименование, адрес

Заказы покупателей (orders, order_items) - возможность заказать разные товары

2. Реализованы SQL запросы
2.1. Сумма товаров по клиентам
sql
SELECT 
    c.name as client_name,
    SUM(oi.quantity * p.price) as total_amount
FROM clients c
JOIN orders o ON o.client_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
GROUP BY c.id, c.name;
2.2. Количество дочерних элементов 1-го уровня
sql
SELECT 
    parent.name as category_name,
    COUNT(child.id) as child_count
FROM categories parent
LEFT JOIN categories child ON child.parent_id = parent.id
GROUP BY parent.id, parent.name;
2.3.1. Топ-5 самых покупаемых товаров за последний месяц
sql
WITH RECURSIVE category_tree AS (
    SELECT id, parent_id, name, name as root_name, 0 as level
    FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.parent_id, c.name, ct.root_name, ct.level + 1
    FROM categories c JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT 
    p.name as product_name,
    ct.root_name as top_level_category,
    SUM(oi.quantity) as total_sold
FROM products p
JOIN order_items oi ON oi.product_id = p.id
JOIN orders o ON o.id = oi.order_id
LEFT JOIN category_tree ct ON p.category_id = ct.id
WHERE o.created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
  AND o.created_at < DATE_TRUNC('month', CURRENT_DATE)
GROUP BY p.id, p.name, ct.root_name
ORDER BY total_sold DESC
LIMIT 5;
3. Реализован REST API сервис
Основной endpoint:

http
POST /api/v1/orders/{order_id}/items
Content-Type: application/json

{
    "product_id": "uuid",
    "quantity": 2
}