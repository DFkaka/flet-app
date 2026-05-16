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
    # Android: 优先从 APK 内置复制
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

    # 桌面：共享数据库
    shared = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'inventory.db')
    if os.path.exists(shared):
        _ensure_tables(shared)
        return shared

    # 本地副本
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

    # 直接显示启动状态
    status = ft.Text('加载中...', size=16)
    page.add(status)
    page.update()

    # 查找数据库
    db_path = _find_db()
    status.value = f'数据库: {"找到" if db_path else "未找到"}'
    page.update()

    if not db_path:
        status.value = '未找到数据库文件，请将 inventory.db 放入应用目录'
        page.update()
        return

    set_db_path(db_path)

    # 去除测试文本
    page.clean()

    detail_id_store: dict = {}

    def navigate(route: str, param=None):
        routes = ('product_detail', 'inventory_detail', 'purchase_detail', 'sales_detail')
        if route in routes and param is not None:
            detail_id_store['value'] = param
        page.go(f'/{route}' if not route.startswith('/') else route)

    def route_change(e):
        route = page.route
        detail_id = detail_id_store.get('value')

        if route in ('/', '/dashboard'):
            view = DashboardView(page, navigate).build()
        elif route == '/products':
            view = ProductsView(page, navigate).build()
        elif route == '/product_detail' and detail_id is not None:
            view = ProductDetailView(page, detail_id).build()
        elif route == '/inventory':
            view = InventoryView(page, navigate).build()
        elif route == '/inventory_detail' and detail_id is not None:
            view = InventoryDetailView(page, detail_id).build()
        elif route == '/purchases':
            view = PurchasesView(page, navigate).build()
        elif route == '/purchase_detail' and detail_id is not None:
            view = PurchaseDetailView(page, detail_id).build()
        elif route == '/sales':
            view = SalesView(page, navigate).build()
        elif route == '/sales_detail' and detail_id is not None:
            view = SalesDetailView(page, detail_id).build()
        else:
            view = DashboardView(page, navigate).build()

        page.views.clear()
        page.views.append(view)

        b1 = ft.IconButton(icon=I.DASHBOARD, icon_size=22)
        b1.on_click = lambda _: page.go('/dashboard')
        b2 = ft.IconButton(icon=I.SEARCH, icon_size=22)
        b2.on_click = lambda _: page.go('/products')
        b3 = ft.IconButton(icon=I.INVENTORY, icon_size=22)
        b3.on_click = lambda _: page.go('/inventory')
        b4 = ft.IconButton(icon=I.SHOPPING_CART, icon_size=22)
        b4.on_click = lambda _: page.go('/purchases')
        b5 = ft.IconButton(icon=I.TRENDING_UP, icon_size=22)
        b5.on_click = lambda _: page.go('/sales')
        view.bottom_appbar = ft.BottomAppBar(
            content=ft.Row([b1, b2, b3, b4, b5], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=C.WHITE,
        )
        page.update()

    page.on_route_change = route_change
    page.go('/dashboard')


ft.app(target=main)
