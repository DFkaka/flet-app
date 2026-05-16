"""Flet 版本兼容层（Colors/Icons 大小写统一）"""

import flet as ft


def _get_colors():
    """获取 colors 模块（兼容 ft.Colors / ft.colors）"""
    if hasattr(ft, 'colors'):
        return ft.colors
    return ft.Colors


def _get_icons():
    """获取 icons 模块（兼容 ft.Icons / ft.icons）"""
    if hasattr(ft, 'icons'):
        return ft.icons
    return ft.Icons


C = _get_colors()
I = _get_icons()
