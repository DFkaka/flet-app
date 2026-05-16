import flet as ft
from components.theme import C, I
from models import get_inventory_list, get_inventory_detail, adjust_inventory, get_inventory_log
from components.data_list import data_row, empty_state, detail_row, section_header
from components.app_bar import create_app_bar


class InventoryView:
    def __init__(self, page: ft.Page, navigate):
        self.page = page
        self.navigate = navigate
        self.filter_type = 'all'
        self.list_container = ft.Container(expand=True)

    def on_filter_change(self, filter_type: str):
        self.filter_type = filter_type
        self.refresh()

    def refresh(self):
        results = get_inventory_list(self.filter_type)
        label_map = {'all': '全部', 'low': '低库存', 'zero': '缺货'}
        title = label_map.get(self.filter_type, '全部')
        items = []
        for p in results:
            qty = p.get('quantity', 0)
            safety = p.get('safety_stock', 0)
            row = data_row(
                leading_text=p['name'][:2] if p.get('name') else p.get('code', '??'),
                title=p['name'] or p.get('code', ''),
                subtitle=f"库存: {qty}  安全库存: {safety}",
                trailing_text=str(qty),
            )
            row.on_click = lambda _, pid=p['id']: self.navigate('inventory_detail', pid)
            items.append(row)
        content_list = [ft.Text(f'{title} ({len(results)} 项)', size=13, color=C.GREY_600)]
        content_list.extend(items if items else [empty_state('暂无库存数据')])
        self.list_container.content = ft.Column(content_list, spacing=0)
        self.page.update()

    def build(self) -> ft.View:
        chip_all = ft.Chip(label=ft.Text('全部'), selected=self.filter_type == 'all')
        chip_all.on_select = lambda _: self.on_filter_change('all')
        chip_low = ft.Chip(label=ft.Text('低库存'), selected=self.filter_type == 'low')
        chip_low.on_select = lambda _: self.on_filter_change('low')
        chip_zero = ft.Chip(label=ft.Text('缺货'), selected=self.filter_type == 'zero')
        chip_zero.on_select = lambda _: self.on_filter_change('zero')

        v = ft.View("/inventory")
        v.appbar = create_app_bar('库存查询')
        v.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Row([chip_all, chip_low, chip_zero], spacing=5),
                    self.list_container,
                ], spacing=10),
                padding=10, expand=True,
            ),
        ]
        return v


class InventoryDetailView:
    def __init__(self, page: ft.Page, product_id: int):
        self.page = page
        self.product_id = product_id
        self.adjust_field = ft.TextField(
            label='调整数量（正数入库，负数出库）',
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200, height=45,
        )
        self.remark_field = ft.TextField(
            label='调整原因', width=200, height=45,
        )
        self.result_text = ft.Text('', color=C.GREEN_700)

    def on_adjust(self, e):
        try:
            delta = int(self.adjust_field.value or '0')
        except ValueError:
            self.result_text.value = '请输入有效数字'
            self.result_text.color = C.RED_600
            self.page.update()
            return
        if delta == 0:
            self.result_text.value = '调整数量不能为 0'
            self.result_text.color = C.RED_600
            self.page.update()
            return
        remark = self.remark_field.value or ''
        ok = adjust_inventory(self.product_id, delta, remark)
        if ok:
            sign = '+' if delta > 0 else ''
            self.result_text.value = f'调整成功！库存已 {sign}{delta}'
            self.result_text.color = C.GREEN_700
            self.adjust_field.value = ''
            self.remark_field.value = ''
        else:
            self.result_text.value = '调整失败（库存不能为负）'
            self.result_text.color = C.RED_600
        self.page.update()

    def build(self) -> ft.View:
        p = get_inventory_detail(self.product_id)
        if not p:
            v = ft.View("/inventory_detail")
            v.appbar = create_app_bar('库存详情')
            v.controls = [empty_state('商品不存在')]
            return v

        logs = get_inventory_log(self.product_id)
        log_items = []
        for log in logs:
            d = log['delta']
            sign = '+' if d >= 0 else ''
            log_items.append(data_row(
                leading_text='调整',
                title=f"{sign}{d}  ( {log['before_qty']} → {log['after_qty']} )",
                subtitle=f"{log['remark'] or '无备注'}  |  {log['created_at']}",
            ))

        adjust_btn = ft.ElevatedButton('执行调整', icon=I.SAVE,
                                      color=C.WHITE, bgcolor=C.BLUE_700)
        adjust_btn.on_click = self.on_adjust

        detail_section = [
            detail_row('商品', p.get('name')),
            detail_row('编码', p.get('code')),
            detail_row('当前库存', str(p.get('stock_quantity', 0))),
            detail_row('安全库存', str(p.get('safety_stock', 0))),
            section_header('库存调整'),
            ft.Row([self.adjust_field], wrap=True),
            ft.Row([self.remark_field], wrap=True),
            adjust_btn,
            self.result_text,
            section_header('调整记录'),
        ]
        detail_section.extend(log_items if log_items else [empty_state('暂无调整记录')])

        v = ft.View("/inventory_detail")
        v.appbar = create_app_bar('库存详情')
        v.controls = [
            ft.Container(
                content=ft.Column(detail_section, spacing=5, scroll=ft.ScrollMode.AUTO),
                padding=15, expand=True,
            ),
        ]
        v.scroll = ft.ScrollMode.AUTO
        return v
