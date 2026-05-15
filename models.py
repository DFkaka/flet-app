"""命名查询封装，所有 SQL 语句集中管理"""

from db import query, get, DatabaseError


# ═══ 看板 ═══

def get_dashboard_stats() -> dict:
    stats = {}
    row = query("SELECT COUNT(*) as c FROM products", ())
    stats['product_count'] = row[0]['c']
    row = query("SELECT COUNT(*) as c FROM purchase_orders WHERE status != 'cancelled'", ())
    stats['purchase_count'] = row[0]['c']
    row = query("SELECT COUNT(*) as c FROM sales_orders WHERE status != 'cancelled'", ())
    stats['sales_count'] = row[0]['c']
    row = query("SELECT COUNT(*) as c FROM inventory WHERE quantity <= safety_stock", ())
    stats['low_stock_count'] = row[0]['c']
    from datetime import date
    m = date.today().strftime('%Y-%m')
    row = query("SELECT COALESCE(SUM(total_amount),0) as t FROM purchase_orders WHERE status='received' AND order_date LIKE ?", (m+'%',))
    stats['month_purchase'] = round(row[0]['t'], 2)
    row = query("SELECT COALESCE(SUM(total_amount),0) as t FROM sales_orders WHERE status='shipped' AND order_date LIKE ?", (m+'%',))
    stats['month_sales'] = round(row[0]['t'], 2)
    row = query("SELECT COALESCE(SUM(i.quantity * p.cost_price),0) as t FROM inventory i JOIN products p ON p.id=i.product_id", ())
    stats['inventory_value'] = round(row[0]['t'], 2)
    return stats


def get_recent_orders() -> list[dict]:
    sql = """
    SELECT '采购' as type, id, order_no, supplier as party, order_date, total_amount, status
    FROM purchase_orders
    WHERE date(order_date) >= date('now','localtime','-5 days')
    UNION ALL
    SELECT '销售' as type, id, order_no, customer as party, order_date, total_amount, status
    FROM sales_orders
    WHERE date(order_date) >= date('now','localtime','-5 days')
    ORDER BY order_date DESC, order_no DESC
    """
    return query(sql, ())


# ═══ 商品 ═══

def search_products(keyword: str) -> list[dict]:
    like = f'%{keyword}%'
    sql = """
    SELECT p.id, p.code, p.name, p.barcode, p.retail_price, p.cost_price,
           c.name as category_name
    FROM products p LEFT JOIN categories c ON c.id = p.category_id
    WHERE p.code=? OR p.barcode=? OR p.name LIKE ? OR p.pinyin_code LIKE ?
    ORDER BY p.name LIMIT 50
    """
    return query(sql, (keyword, keyword, like, like))


def get_product_detail(product_id: int) -> dict | None:
    sql = """
    SELECT p.*, c.name as category_name,
           COALESCE(i.quantity,0) as stock_quantity, i.safety_stock
    FROM products p
    LEFT JOIN categories c ON c.id = p.category_id
    LEFT JOIN inventory i ON i.product_id = p.id
    WHERE p.id = ?
    """
    return get(sql, (product_id,))


# ═══ 库存 ═══

def get_inventory_list(filter_type: str = 'all') -> list[dict]:
    sql = """
    SELECT p.id, p.code, p.name, p.barcode,
           COALESCE(i.quantity,0) as quantity, COALESCE(i.safety_stock,0) as safety_stock
    FROM products p LEFT JOIN inventory i ON i.product_id = p.id
    """
    if filter_type == 'low':
        sql += " WHERE COALESCE(i.quantity,0) <= COALESCE(i.safety_stock,0)"
    elif filter_type == 'zero':
        sql += " WHERE COALESCE(i.quantity,0) = 0"
    sql += " ORDER BY p.name"
    return query(sql, ())


def get_inventory_detail(product_id: int) -> dict | None:
    return get_product_detail(product_id)


def adjust_inventory(product_id: int, delta: int, remark: str) -> bool:
    from db import transaction
    cur = get("SELECT quantity FROM inventory WHERE product_id=?", (product_id,))
    current_qty = cur['quantity'] if cur else 0
    new_qty = current_qty + delta
    if new_qty < 0:
        return False
    try:
        with transaction() as conn:
            if cur:
                conn.execute("UPDATE inventory SET quantity=? WHERE product_id=?", (new_qty, product_id))
            else:
                conn.execute("INSERT INTO inventory (product_id,quantity) VALUES (?,?)", (product_id, new_qty))
            conn.execute(
                "INSERT INTO inventory_log (product_id,delta,before_qty,after_qty,remark,created_at) "
                "VALUES (?,?,?,?,?,datetime('now','localtime'))",
                (product_id, delta, current_qty or 0, new_qty, remark)
            )
        return True
    except DatabaseError:
        return False


def get_inventory_log(product_id: int) -> list[dict]:
    sql = """
    SELECT id, delta, before_qty, after_qty, remark, created_at
    FROM inventory_log WHERE product_id=? ORDER BY id DESC LIMIT 20
    """
    return query(sql, (product_id,))


# ═══ 采购单 ═══

def get_purchase_orders(date_from: str = '', date_to: str = '',
                        supplier: str = '', status: str = '') -> list[dict]:
    conditions = []
    params = []
    if date_from:
        conditions.append("date(order_date) >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date(order_date) <= ?")
        params.append(date_to)
    if supplier:
        conditions.append("supplier LIKE ?")
        params.append(f'%{supplier}%')
    if status:
        conditions.append("status = ?")
        params.append(status)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f"""
    SELECT id, order_no, supplier, order_date, status, total_amount, payment_status
    FROM purchase_orders {where}
    ORDER BY id DESC LIMIT 50
    """
    return query(sql, tuple(params))


def get_purchase_detail(order_id: int) -> dict | None:
    order = get(
        "SELECT id,order_no,supplier,order_date,status,"
        "total_amount,paid_amount,payment_status,note as remark "
        "FROM purchase_orders WHERE id=?", (order_id,)
    )
    if not order:
        return None
    order['items'] = query(
        """SELECT poi.*, p.name as product_name, p.code as product_code
           FROM purchase_order_items poi
           LEFT JOIN products p ON p.id=poi.product_id
           WHERE poi.order_id=?""",
        (order_id,)
    )
    order['payments'] = query(
        "SELECT id,payer,payment_date,amount,note "
        "FROM purchase_payments WHERE order_id=? ORDER BY id",
        (order_id,)
    )
    return order


# ═══ 销售单 ═══

def get_sales_orders(date_from: str = '', date_to: str = '',
                     customer: str = '', status: str = '') -> list[dict]:
    conditions = []
    params = []
    if date_from:
        conditions.append("date(order_date) >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date(order_date) <= ?")
        params.append(date_to)
    if customer:
        conditions.append("customer LIKE ?")
        params.append(f'%{customer}%')
    if status:
        conditions.append("status = ?")
        params.append(status)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f"""
    SELECT id, order_no, customer, order_date, status, total_amount, payment_status
    FROM sales_orders {where}
    ORDER BY id DESC LIMIT 50
    """
    return query(sql, tuple(params))


def get_sales_detail(order_id: int) -> dict | None:
    order = get(
        "SELECT id,order_no,customer,order_date,status,"
        "total_amount,paid_amount,payment_status,note as remark "
        "FROM sales_orders WHERE id=?", (order_id,)
    )
    if not order:
        return None
    order['items'] = query(
        """SELECT soi.*, p.name as product_name, p.code as product_code
           FROM sales_order_items soi
           LEFT JOIN products p ON p.id=soi.product_id
           WHERE soi.order_id=?""",
        (order_id,)
    )
    order['payments'] = query(
        "SELECT id,payer,payment_date,amount,note "
        "FROM sales_payments WHERE order_id=? ORDER BY id",
        (order_id,)
    )
    return order
