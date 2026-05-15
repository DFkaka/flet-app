import flet as ft
from models import search_products, get_product_detail
from components.data_list import data_row, empty_state, detail_row, section_header
from components.app_bar import create_app_bar


class ProductsView:
    def __init__(self, page: ft.Page, navigate):
        self.page = page
        self.navigate = navigate
        self.search_field = ft.TextField(
            hint_text='搜索商品（名称/编码/条码）',
            prefix_icon=ft.icons.SEARCH,
            border_radius=10,
            text_size=14,
            height=45,
        )
        self.search_field.on_change = self.on_search
        self.list_container = ft.Container(expand=True)

    def on_search(self, e):
        keyword = self.search_field.value.strip()
        if not keyword:
            self.list_container.content = empty_state('输入关键词搜索商品')
            self.page.update()
            return
        results = search_products(keyword)
        items = []
        for p in results:
            items.append(data_row(
                leading_text=p['name'][:2] if p['name'] else p['code'],
                title=p['name'] or '',
                subtitle=f"编码: {p['code']}  |  零售: ¥{p['retail_price']}" if p['retail_price'] else f"编码: {p['code']}",
                trailing_text=f"¥{p['retail_price']}" if p['retail_price'] else '',
                on_click=lambda _, pid=p['id']: self.navigate('product_detail', pid),
            ))
        self.list_container.content = ft.Column(
            items if items else [empty_state('未找到匹配商品')],
            spacing=0,
        )
        self.page.update()

    def build(self) -> ft.View:
        v = ft.View("/products")
        v.appbar = create_app_bar('商品查询')
        v.controls = [
            ft.Container(
                content=ft.Column([
                    self.search_field,
                    self.list_container,
                ], spacing=10),
                padding=10, expand=True,
            ),
        ]
        return v


class ProductDetailView:
    def __init__(self, page: ft.Page, product_id: int):
        self.page = page
        self.product_id = product_id

    def build(self) -> ft.View:
        p = get_product_detail(self.product_id)
        if not p:
            v = ft.View("/product_detail")
            v.appbar = create_app_bar('商品详情')
            v.controls = [ft.Container(empty_state('商品不存在'), padding=20)]
            return v

        detail_items = [
            detail_row('商品名称', p.get('name')),
            detail_row('编码', p.get('code')),
            detail_row('条码', p.get('barcode')),
            detail_row('类别', p.get('category_name')),
            detail_row('零售价', f"¥{p['retail_price']}" if p.get('retail_price') else '-'),
            detail_row('成本价', f"¥{p['cost_price']}" if p.get('cost_price') else '-'),
            detail_row('拼音码', p.get('pinyin_code')),
            detail_row('规格', p.get('spec')),
            detail_row('单位', p.get('unit')),
            section_header('库存信息'),
            detail_row('当前库存', str(p.get('stock_quantity', 0))),
            detail_row('安全库存', str(p.get('safety_stock', 0))),
        ]

        v = ft.View("/product_detail")
        v.appbar = create_app_bar('商品详情')
        v.controls = [
            ft.Container(
                content=ft.Column(detail_items, spacing=3, scroll=ft.ScrollMode.AUTO),
                padding=15, expand=True,
            ),
        ]
        v.scroll = ft.ScrollMode.AUTO
        return v
