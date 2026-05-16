import flet as ft
from components.theme import C, I
from models import get_dashboard_stats, get_recent_orders
from components.stat_card import stat_card
from components.data_list import data_row, section_header, empty_state
from components.app_bar import create_app_bar


class DashboardView:
    def __init__(self, page: ft.Page, navigate):
        self.page = page
        self.navigate = navigate

    def build(self) -> ft.View:
        stats = get_dashboard_stats()
        recent_orders = get_recent_orders()

        stat_row = ft.ResponsiveRow([
            ft.Container(stat_card('商品总数', str(stats.get('product_count', 0)),
                                   I.INVENTORY, C.BLUE_700),
                        col={"xs": 6}),
            ft.Container(stat_card('库存预警', str(stats.get('low_stock_count', 0)),
                                   I.WARNING_AMBER, C.RED_600),
                        col={"xs": 6}),
            ft.Container(stat_card('本月采购', f'¥{stats.get("month_purchase", 0):.0f}',
                                   I.SHOPPING_CART, C.GREEN_700),
                        col={"xs": 6}),
            ft.Container(stat_card('本月销售', f'¥{stats.get("month_sales", 0):.0f}',
                                   I.TRENDING_UP, C.ORANGE_700),
                        col={"xs": 6}),
        ], spacing=10, run_spacing=10)

        stats_row2 = ft.ResponsiveRow([
            ft.Container(stat_card('库存总值', f'¥{stats.get("inventory_value", 0):.0f}',
                                   I.ACCOUNT_BALANCE, C.PURPLE_700),
                        col={"xs": 12}),
        ], spacing=10)

        recent_items = []
        for order in recent_orders:
            order_id = order['id']
            if order['type'] == '采购':
                target_route = 'purchase_detail'
            else:
                target_route = 'sales_detail'
            color = C.GREEN_700 if order['type'] == '采购' else C.RED_600
            party_name = order['party'].split(' ', 1)[-1] if ' ' in order['party'] else order['party']
            status_map = {'shipped': '已出库', 'received': '已收货', 'draft': '草稿', 'pending': '待处理', 'cancelled': '已取消'}
            status_text = status_map.get(order['status'], order['status'])
            row = data_row(
                leading_text=order['type'],
                title=f"{order['order_no']} - {party_name} - {status_text}",
                subtitle=f"{order['order_date']}  ¥{order['total_amount']:.0f}",
                trailing_text='',
                avatar_color=color,
            )
            row.on_click = lambda _, oid=order_id, route=target_route: self.navigate(route, oid)
            recent_items.append(row)

        recent_section = recent_items if recent_items else [empty_state()]

        v = ft.View("/dashboard")
        v.appbar = create_app_bar('进销存查询')
        v.controls = [
            ft.Container(
                content=ft.Column([
                    stat_row,
                    stats_row2 if stats else ft.Container(),
                    section_header('最近业务动态'),
                    *recent_section,
                ], spacing=5, scroll=ft.ScrollMode.AUTO),
                padding=10, expand=True,
            ),
        ]
        v.scroll = ft.ScrollMode.AUTO
        return v
