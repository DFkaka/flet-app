import flet as ft


def create_app_bar(title: str = '进销存查询') -> ft.AppBar:
    return ft.AppBar(
        title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
        center_title=True,
        bgcolor=ft.colors.BLUE_700,
        color=ft.colors.WHITE,
    )
