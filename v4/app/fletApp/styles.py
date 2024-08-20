# styles.py
import flet as ft

def button_style():
    return ft.ButtonStyle(
        bgcolor={"hovered": ft.colors.RED_700, "": ft.colors.RED_500},  # Alterado para vermelho
        color={"": ft.colors.WHITE},
        padding=ft.Padding(
            top=12, bottom=12, left=24, right=24
        ),
        shape=ft.RoundedRectangleBorder(radius=8),
    )
