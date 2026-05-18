"""远程数据层 - 通过 HTTP 调用 Flask API 获取数据"""

from api_client import api


def get_dashboard_stats() -> dict:
    data = api.api_get('/api/dashboard')
    return data or {}


def get_recent_orders() -> list[dict]:
    return []


def search_products(keyword: str) -> list[dict]:
    data = api.api_get(f'/api/search?q={keyword}')
    if data and 'results' in data:
        return data['results'].get('products', [])
    return []


def get_product_detail(product_id: int) -> dict | None:
    data = api.api_get(f'/api/products/{product_id}')
    return data if data else None


def get_inventory_list(filter_type: str = 'all') -> list[dict]:
    data = api.api_get('/api/inventory')
    return data if data else []


def get_inventory_detail(product_id: int) -> dict | None:
    return get_product_detail(product_id)


def adjust_inventory(product_id: int, delta: int, remark: str) -> bool:
    return False  # 远程模式不支持库存调整


def get_inventory_log(product_id: int) -> list[dict]:
    return []


def get_purchase_orders(date_from='', date_to='', supplier='', status='') -> list[dict]:
    params = {}
    if date_from: params['date_from'] = date_from
    if date_to: params['date_to'] = date_to
    if supplier: params['supplier'] = supplier
    if status: params['status'] = status
    qs = '&'.join(f'{k}={v}' for k, v in params.items())
    data = api.api_get(f'/api/purchase-orders?{qs}' if qs else '/api/purchase-orders')
    return data if data else []


def get_purchase_detail(order_id: int) -> dict | None:
    data = api.api_get(f'/api/purchase-orders/{order_id}')
    return data if data else None


def get_sales_orders(date_from='', date_to='', customer='', status='') -> list[dict]:
    params = {}
    if date_from: params['date_from'] = date_from
    if date_to: params['date_to'] = date_to
    if customer: params['customer'] = customer
    if status: params['status'] = status
    qs = '&'.join(f'{k}={v}' for k, v in params.items())
    data = api.api_get(f'/api/sales-orders?{qs}' if qs else '/api/sales-orders')
    return data if data else []


def get_sales_detail(order_id: int) -> dict | None:
    data = api.api_get(f'/api/sales-orders/{order_id}')
    return data if data else None
