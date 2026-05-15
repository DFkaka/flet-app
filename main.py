"""进销存查询 App — Flet Android 主入口"""

import os
import sys
import shutil
import sqlite3
import traceback
import flet as ft

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import set_db_path
from views.dashboard import DashboardView
from views.products import ProductsView, ProductDetailView
from views.inventory import InventoryView, InventoryDetailView
from views.purchases import PurchasesView, PurchaseDetailView
from views.sales import SalesView, SalesDetailView

DB_FILENAME = 'inventory_app.db'


def _get_app_data_dir() -> str:
    android_path = '/data/data/com.dfpos.inventory/files'
    if os.path.exists(android_path):
        return android_path
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(local_path, exist_ok=True)
    return local_path


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
    """查找可用的数据库文件"""
    # 1. 桌面：直接使用和 app.py 共享的数据库
    shared = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'inventory.db')
    if os.path.exists(shared):
        _ensure_tables(shared)
        return shared

    # 2. APK 内 bundled（仅 Android）
    app_dir = _get_app_data_dir()
    bundled = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.db')
    if os.path.exists(bundled):
        os.makedirs(app_dir, exist_ok=True)
        cached = os.path.join(app_dir, DB_FILENAME)
        shutil.copy2(bundled, cached)
        _ensure_tables(cached)
        return cached

    return ''


def main(page: ft.Page):
    try:
        page.title = '进销存查询'
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.window.width = 400
        page.window.height = 780

        # 查找数据库
        db_path = _find_db()
        if not db_path:
            page.add(ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ERROR_OUTLINE, size=64, color=ft.colors.RED_600),
                    ft.Text('找不到数据库文件', size=20, weight=ft.FontWeight.BOLD),
                    ft.Text('请将 inventory.db 放到应用目录', size=14, color=ft.colors.GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                padding=50, alignment=ft.alignment.Alignment(0, 0), expand=True,
            ))
            page.update()
            return

        set_db_path(db_path)

        # 共享状态
        detail_id_store: dict = {}

        def navigate(route: str, param=None):
            if route in ('product_detail', 'inventory_detail', 'purchase_detail', 'sales_detail'):
                if param is not None:
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

            b1 = ft.IconButton(icon=ft.icons.DASHBOARD, icon_size=22)
            b1.on_click = lambda _: page.go('/dashboard')
            b2 = ft.IconButton(icon=ft.icons.SEARCH, icon_size=22)
            b2.on_click = lambda _: page.go('/products')
            b3 = ft.IconButton(icon=ft.icons.INVENTORY, icon_size=22)
            b3.on_click = lambda _: page.go('/inventory')
            b4 = ft.IconButton(icon=ft.icons.SHOPPING_CART, icon_size=22)
            b4.on_click = lambda _: page.go('/purchases')
            b5 = ft.IconButton(icon=ft.icons.TRENDING_UP, icon_size=22)
            b5.on_click = lambda _: page.go('/sales')
            view.bottom_appbar = ft.BottomAppBar(
                content=ft.Row([b1, b2, b3, b4, b5], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                bgcolor=ft.colors.WHITE,
            )
            page.views.clear()
            page.views.append(view)
            page.update()

        page.on_route_change = route_change
        page.go('/dashboard')

    except Exception as e:
        # 显示错误信息，防止闪退
        page.add(ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.ERROR, size=48, color=ft.colors.RED_600),
                ft.Text('启动失败', size=18, weight=ft.FontWeight.BOLD),
                ft.Text(str(e), size=12, color=ft.colors.RED_700, selectable=True),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=30, expand=True, alignment=ft.alignment.Alignment(0, 0),
        ))
        page.update()


ft.app(target=main)
