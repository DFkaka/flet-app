"""进销存查询 App — Flet Android 主入口"""

import os
import sys
import shutil
import sqlite3
import flet as ft
from components.theme import C, I

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import set_db_path
from views.dashboard import DashboardView
from views.products import ProductsView, ProductDetailView
from views.inventory import InventoryView, InventoryDetailView
from views.purchases import PurchasesView, PurchaseDetailView
from views.sales import SalesView, SalesDetailView

DB_FILENAME = 'inventory_app.db'


def _ensure_tables(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS inventory_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        delta REAL NOT NULL,
        before_qty REAL NOT NULL,
        after_qty REAL NOT NULL,
        remark TEXT,
        created_at TEXT
    )""")
    conn.commit()
    conn.close()


def _find_db() -> str:
    app_dir = '/data/data/com.dfpos.dfpos_inventory/files'
    cached = os.path.join(app_dir, DB_FILENAME)
    if os.path.exists(cached):
        return cached
    bundled = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.db')
    if os.path.exists(bundled):
        os.makedirs(app_dir, exist_ok=True)
        shutil.copy2(bundled, cached)
        _ensure_tables(cached)
        return cached
    shared = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'inventory.db')
    if os.path.exists(shared):
        _ensure_tables(shared)
        return shared
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.db')
    if os.path.exists(local):
        return local
    return ''


def main(page: ft.Page):
    page.title = '进销存查询'
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window.width = 400
    page.window.height = 780

    # 初始化数据库
    db_path = _find_db()
    if not db_path:
        # 创建空数据库（确保 App 能启动）
        empty_path = '/data/data/com.dfpos.dfpos_inventory/files/inventory_app.db'
        os.makedirs(os.path.dirname(empty_path), exist_ok=True)
        conn = sqlite3.connect(empty_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, code TEXT, name TEXT, barcode TEXT, retail_price REAL, cost_price REAL);
            CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT);
            CREATE TABLE IF NOT EXISTS purchase_orders (id INTEGER PRIMARY KEY, order_no TEXT, supplier TEXT, order_date TEXT, status TEXT, total_amount REAL, payment_status TEXT);
            CREATE TABLE IF NOT EXISTS sales_orders (id INTEGER PRIMARY KEY, order_no TEXT, customer TEXT, order_date TEXT, status TEXT, total_amount REAL, payment_status TEXT);
            CREATE TABLE IF NOT EXISTS inventory (product_id INTEGER PRIMARY KEY, quantity REAL, safety_stock REAL);
            CREATE TABLE IF NOT EXISTS purchase_order_items (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity REAL, unit_price REAL, subtotal REAL);
            CREATE TABLE IF NOT EXISTS sales_order_items (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity REAL, unit_price REAL, subtotal REAL);
            CREATE TABLE IF NOT EXISTS purchase_payments (id INTEGER PRIMARY KEY, order_id INTEGER, payer TEXT, payment_date TEXT, amount REAL);
            CREATE TABLE IF NOT EXISTS sales_payments (id INTEGER PRIMARY KEY, order_id INTEGER, payer TEXT, payment_date TEXT, amount REAL);
            CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY, code TEXT, name TEXT);
            CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, code TEXT, name TEXT);
        """)
        _ensure_tables(empty_path)
        conn.commit()
        conn.close()
        db_path = empty_path
    set_db_path(db_path)

    # 容器：页面标题
    appbar = ft.Container(
        content=ft.Text('进销存查询', size=18, weight=ft.FontWeight.BOLD, color=C.WHITE),
        padding=15, bgcolor=C.BLUE_700, alignment=ft.alignment.center,
    )

    # 容器：内容区域
    content_area = ft.Container(expand=True, padding=10)

    # 底部导航
    current_tab = 0

    def switch_tab(index):
        nonlocal current_tab
        current_tab = index
        routes = ['/dashboard', '/products', '/inventory', '/purchases', '/sales']
        page.route = routes[index]
        # 清除旧内容并加载新页面
        content_area.content = None
        page.update()

        # 构建新视图
        try:
            if index == 0:
                v = DashboardView(page, lambda r, p=None: None).build()
            elif index == 1:
                v = ProductsView(page, lambda r, p=None: None).build()
            elif index == 2:
                v = InventoryView(page, lambda r, p=None: None).build()
            elif index == 3:
                v = PurchasesView(page, lambda r, p=None: None).build()
            elif index == 4:
                v = SalesView(page, lambda r, p=None: None).build()
            # 提取实际内容（跳过 AppBar，只取内容容器）
            content_area.content = ft.Column(
                [c for c in (v.controls or []) if not isinstance(c, ft.AppBar)],
                expand=True, scroll=ft.ScrollMode.AUTO,
            )
            page.update()
        except Exception as ex:
            import traceback
            content_area.content = ft.Column([
                ft.Text(f'错误: {type(ex).__name__}: {ex}', color=C.RED_600, selectable=True),
                ft.Text(traceback.format_exc(), size=10, color=C.GREY_600, selectable=True),
            ], scroll=ft.ScrollMode.AUTO)
            page.update()

    nav_icons = [I.DASHBOARD, I.SEARCH, I.INVENTORY, I.SHOPPING_CART, I.TRENDING_UP]
    nav_btns = []
    for i, icon in enumerate(nav_icons):
        btn = ft.IconButton(icon=icon, icon_size=22)
        btn.on_click = lambda _, idx=i: switch_tab(idx)
        nav_btns.append(btn)

    navbar = ft.Container(
        content=ft.Row(nav_btns, alignment=ft.MainAxisAlignment.SPACE_AROUND),
        padding=5, bgcolor=C.WHITE, border=ft.border.only(top=ft.BorderSide(1, C.GREY_300)),
    )

    # 组装页面
    page.add(
        ft.Column([
            appbar,
            content_area,
            navbar,
        ], spacing=0, expand=True)
    )
    page.update()

    # 默认加载看板
    switch_tab(0)


ft.app(target=main)
