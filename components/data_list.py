import flet as ft
from components.theme import C, I


def data_row(leading_text: str, title: str, subtitle: str, trailing_text: str = '',
             on_click=None, avatar_color=C.BLUE_700) -> ft.Container:
    """通用数据行组件"""
    return ft.Container(
        content=ft.ListTile(
            leading=ft.Container(
                content=ft.Text(leading_text[:2], size=14, weight=ft.FontWeight.BOLD,
                               color=C.WHITE),
                width=40, height=40,
                bgcolor=avatar_color,
                border_radius=20,
                alignment=ft.alignment.Alignment(0, 0),
            ),
            title=ft.Text(title, size=15, weight=ft.FontWeight.W_500),
            subtitle=ft.Text(subtitle, size=12, color=C.GREY_600),
            trailing=ft.Text(trailing_text, size=13, color=C.GREY_700)
            if trailing_text else None,
            on_click=on_click,
        ),
            )


def section_header(title: str) -> ft.Container:
    """段落标题"""
    return ft.Container(
        content=ft.Text(title, size=14, weight=ft.FontWeight.BOLD,
                       color=C.BLUE_700),
        padding=ft.Padding(left=10, top=15, right=0, bottom=5),
    )


def empty_state(message: str = '暂无数据') -> ft.Container:
    """空状态提示"""
    return ft.Container(
        content=ft.Column([
            ft.Icon(I.INBOX, size=48, color=C.GREY_400),
            ft.Text(message, color=C.GREY_500),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        padding=50,
    )


def status_badge(status: str) -> ft.Container:
    """状态标签"""
    colors = {
        'pending': (C.ORANGE_100, C.ORANGE_900, '待处理'),
        'received': (C.GREEN_100, C.GREEN_900, '已收货'),
        'shipped': (C.GREEN_100, C.GREEN_900, '已发货'),
        'cancelled': (C.RED_100, C.RED_900, '已取消'),
        'draft': (C.GREY_100, C.GREY_900, '草稿'),
    }
    bg, fg, label = colors.get(status, (C.GREY_100, C.GREY_900, status))
    return ft.Container(
        content=ft.Text(label, size=11, color=fg),
        padding=ft.Padding(left=8, right=8, top=3, bottom=3),
        bgcolor=bg,
        border_radius=10,
    )


def detail_row(label: str, value: str) -> ft.Row:
    """详情页字段行"""
    return ft.Row([
        ft.Text(label + '：', size=14, weight=ft.FontWeight.BOLD,
               color=C.GREY_700, width=80),
        ft.Text(value or '-', size=14, expand=True),
    ], spacing=5)
