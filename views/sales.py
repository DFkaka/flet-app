import flet as ft
from models import get_sales_orders, get_sales_detail
from components.data_list import data_row, empty_state, detail_row, section_header, status_badge
from components.app_bar import create_app_bar
from datetime import date


class SalesView:
    def __init__(self, page: ft.Page, navigate):
        self.page = page
        self.navigate = navigate
        today = date.today().strftime('%Y-%m-%d')
        self.date_from = ft.TextField(
            hint_text='开始日期', prefix_icon=ft.icons.DATE_RANGE,
            value=today, height=40, text_size=14, expand=1,
        )
        self.date_to = ft.TextField(
            hint_text='结束日期', prefix_icon=ft.icons.DATE_RANGE,
            value=today, height=40, text_size=14, expand=1,
        )
        self.customer_field = ft.TextField(
            hint_text='客户名称/编码', prefix_icon=ft.icons.SEARCH,
            height=40, text_size=14, expand=1,
        )
        self.customer_field.on_change = self.on_filter_change
        self.status_dd = ft.Dropdown(
            options=[
                ft.dropdown.Option(key='', text='全部状态'),
                ft.dropdown.Option(key='shipped', text='已出库'),
                ft.dropdown.Option(key='draft', text='草稿'),
            ],
            height=40, text_size=14, expand=1,
        )
        self.list_container = ft.Container(expand=True)
        self.search_btn = ft.IconButton(icon=ft.icons.SEARCH, icon_size=22)
        self.search_btn.on_click = self.on_search_click

    def on_filter_change(self, e):
        # TextField text change - auto search
        self.refresh()

    def on_search_click(self, e):
        # Dropdown or manual search button
        self.refresh()

    def refresh(self):
        results = get_sales_orders(
            date_from=self.date_from.value or '',
            date_to=self.date_to.value or '',
            customer=self.customer_field.value or '',
            status=self.status_dd.value or '',
        )
        items = []
        for o in results:
            row = data_row(
                leading_text='销售',
                title=o['order_no'] or '',
                subtitle=f"{o['customer'] or ''}  {o['order_date'] or ''}",
                trailing_text=f"¥{o['total_amount']:.0f}" if o.get('total_amount') else '',
            )
            row.on_click = lambda _, oid=o['id']: self.navigate('sales_detail', oid)
            items.append(row)
        self.list_container.content = ft.Column(items, spacing=0) if items else empty_state('暂无销售单')
        self.page.update()

    def build(self) -> ft.View:
        self.refresh()
        v = ft.View("/sales")
        v.appbar = create_app_bar('销售查询')
        v.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Row([self.date_from, self.date_to], spacing=5),
                    ft.Row([self.customer_field, self.status_dd, self.search_btn], spacing=5),
                    self.list_container,
                ], spacing=10),
                padding=10, expand=True,
            ),
        ]
        return v


class SalesDetailView:
    def __init__(self, page: ft.Page, order_id: int):
        self.page = page
        self.order_id = order_id

    def build(self) -> ft.View:
        o = get_sales_detail(self.order_id)
        if not o:
            v = ft.View("/sales_detail")
            v.appbar = create_app_bar('销售单详情')
            v.controls = [empty_state('销售单不存在')]
            return v

        sections = [
            detail_row('单号', o.get('order_no')),
            detail_row('客户', o.get('customer')),
            detail_row('日期', o.get('order_date')),
            ft.Row([detail_row('金额', f"¥{o['total_amount']}" if o.get('total_amount') else '¥0'),
                    status_badge(o.get('status', ''))], spacing=10),
            detail_row('付款状态', o.get('payment_status')),
            detail_row('备注', o.get('remark')),
        ]

        if o.get('items'):
            sections.append(section_header(f"商品明细 ({len(o['items'])} 项)"))
            for item in o['items']:
                sections.append(ft.Container(
                    content=ft.Column([
                        ft.Text(item.get('product_name', '') or '', weight=ft.FontWeight.W_500),
                        ft.Text(
                            f"数量: {item.get('quantity', 0)}  x  单价: ¥{item.get('unit_price', 0):.2f}"
                            f"  =  ¥{item.get('subtotal', 0):.2f}",
                            size=12, color=ft.colors.GREY_600,
                        ),
                    ]),
                    padding=ft.Padding(left=8, top=8, right=8, bottom=8),
                ))

        if o.get('payments'):
            sections.append(section_header(f"付款记录 ({len(o['payments'])} 笔)"))
            for pay in o['payments']:
                sections.append(data_row(
                    leading_text='付款',
                    title=f"¥{pay.get('amount', 0):.2f}",
                    subtitle=pay.get('payment_date', '') or '',
                ))

        v = ft.View("/sales_detail")
        v.appbar = create_app_bar('销售单详情')
        v.controls = [
            ft.Container(
                content=ft.Column(sections, spacing=3, scroll=ft.ScrollMode.AUTO),
                padding=15, expand=True,
            ),
        ]
        v.scroll = ft.ScrollMode.AUTO
        return v
