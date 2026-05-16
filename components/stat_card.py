import flet as ft
from components.theme import C, I


def stat_card(title: str, value: str, icon: str, color: str = C.BLUE_700) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, color=C.WHITE, size=24),
            ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=C.WHITE),
            ft.Text(title, size=12, color=C.with_opacity(0.85, C.WHITE)),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        padding=15,
        bgcolor=color,
        border_radius=12,
        expand=True,
        animate=200,
    )
