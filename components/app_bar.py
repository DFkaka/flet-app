import flet as ft
from components.theme import C, I


def create_app_bar(title: str = '进销存查询') -> ft.AppBar:
    return ft.AppBar(
        title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
        center_title=True,
        bgcolor=C.BLUE_700,
        color=C.WHITE,
    )
