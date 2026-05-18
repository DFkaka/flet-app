"""进销存查询 App — 远程连接版"""

import os
import sys
import flet as ft
from components.theme import C, I

# 不提前导入 views，等连接成功后导入（确保使用远程数据层）

from api_client import api


def show_login(page: ft.Page, on_success):
    """显示登录设置界面"""
    host_field = ft.TextField(label='电脑 IP 地址', value='192.168.1.', hint_text='如 192.168.1.100')
    port_field = ft.TextField(label='端口号', value='5000', hint_text='Flask 默认端口 5000')
    status_text = ft.Text('', size=13, color=C.RED_600)
    btn = ft.ElevatedButton('连接', icon=I.CLOUD, height=48)
    loading = ft.ProgressBar(width=200, visible=False)

    def on_connect(e):
        host = host_field.value.strip()
        port = port_field.value.strip()
        if not host or not port:
            status_text.value = '请输入 IP 和端口'
            page.update()
            return
        loading.visible = True
        btn.disabled = True
        status_text.value = '连接中...'
        status_text.color = C.GREY_600
        page.update()

        try:
            api.save_settings(host, int(port), 'admin', 'admin')
            if api.logged_in:
                on_success()
            else:
                status_text.value = '连接失败，请检查 IP 和端口'
                status_text.color = C.RED_600
                loading.visible = False
                btn.disabled = False
                page.update()
        except Exception as ex:
            status_text.value = f'连接失败: {ex}'
            status_text.color = C.RED_600
            loading.visible = False
            btn.disabled = False
            page.update()

    btn.on_click = on_connect

    page.add(
        ft.Container(
            ft.Column([
                ft.Icon(I.COMPUTER, size=64, color=C.BLUE_700),
                ft.Text('连接电脑数据库', size=22, weight=ft.FontWeight.BOLD),
                ft.Text('输入电脑上 Flask 服务的 IP 和端口', size=13, color=C.GREY_600),
                ft.Divider(height=20),
                host_field,
                port_field,
                ft.Divider(height=10),
                btn,
                loading,
                status_text,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            padding=30, expand=True,
        )
    )
    page.update()


def main(page: ft.Page):
    page.title = '进销存查询'
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window.width = 400
    page.window.height = 780

    # 尝试自动连接
    connected = api.load_settings()

    if not connected:
        show_login(page, lambda: start_app(page))
        return

    start_app(page)


def start_app(page: ft.Page):
    """连接成功后启动主程序"""
    # 替换 models 为远程版本（views 中 from models import xxx 会取到这里）
    import remote_models
    sys.modules['models'] = remote_models

    # 清除登录页面
    page.clean()

    # 延迟导入视图（确保它们拿到的是 remote_models）
    from views.dashboard import DashboardView
    from views.products import ProductsView, ProductDetailView
    from views.inventory import InventoryView, InventoryDetailView
    from views.purchases import PurchasesView, PurchaseDetailView
    from views.sales import SalesView, SalesDetailView

    # 状态
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
