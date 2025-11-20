1. Спроектировать схему БД
1.1. Номенклатура (наименование, кол-во, цена)

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    price NUMERIC(10,2) NOT NULL,
    category_id UUID REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

1.2. Каталог номенклатуры/Дерево категорий

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

1.3. Клиенты (наименование, адрес)

```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

1.4. Заказы покупателей

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id),
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

```sql
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id),
    product_id UUID NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(order_id, product_id)
);
```

2. SQL запросы
2.1. Получение информации о сумме товаров заказанных под каждого клиента (Наименование клиента, сумма)

```sql
SELECT 
    c.name as client_name,
    SUM(oi.quantity * p.price) as total_amount
FROM clients c
JOIN orders o ON o.client_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
GROUP BY c.id, c.name;
```
2.2. Найти количество дочерних элементов первого уровня вложенности для категорий номенклатуры
```sql
SELECT 
    parent.name as category_name,
    COUNT(child.id) as child_count
FROM categories parent
LEFT JOIN categories child ON child.parent_id = parent.id
GROUP BY parent.id, parent.name;
```
2.3.1. Топ-5 самых покупаемых товаров за последний месяц
```sql
WITH RECURSIVE category_tree AS (
    SELECT 
        id, 
        parent_id, 
        name,
        name as root_name,
        0 as level
    FROM categories 
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT 
        c.id, 
        c.parent_id, 
        c.name,
        ct.root_name,
        ct.level + 1 as level
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
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
```

2.3.2. Анализ оптимизации
Уже реализованные оптимизации:
1. Индексы для ключевых полей.
2. Эффективная структура запроса.
3. Архитектурные оптимизации.

Дополнительные оптимизации для роста данных (тысячи заказов в день):
1. Материализованные представления для отчетов.
2. Денормализация для частых запросов.
3. Кэширование в Redis.
4. Партиционирование для больших объемов.

<img width="531" height="499" alt="image" src="https://github.com/user-attachments/assets/d229f50d-a2e0-4f65-a431-efee3bd0405d" />
