import flet as ft


def stat_card(title: str, value: str, icon: str, color: str = ft.colors.BLUE_700) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, color=ft.colors.WHITE, size=24),
            ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Text(title, size=12, color=ft.colors.with_opacity(0.85, ft.colors.WHITE)),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        padding=15,
        bgcolor=color,
        border_radius=12,
        expand=True,
        animate=200,
    )
