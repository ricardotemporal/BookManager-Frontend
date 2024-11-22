"""
This module implements a Flet application for managing books. 

Features:
- Home page for viewing and registering books.
- Review page for submitting reviews and deleting books.
- Integration with a Django API for backend operations.
"""

import flet as ft
import requests
from connect import get_livros
from urllib.parse import urlparse, parse_qs

def main(page: ft.Page):
    """
    Entry point for the Flet application. Manages routing and views.
    
    Args:
    - page (ft.Page): Main application page.
    """
    page.title = "Book Manager"
    page.window_width = 400

    def home_page():
        """
        Home page for viewing and registering books.
        """
        nome_input = ft.TextField(label="Book Name", text_align=ft.TextAlign.LEFT)

        streaming_select = ft.Dropdown(
            options=[
                ft.dropdown.Option("AK", text="Amazon Kindle"),
                ft.dropdown.Option("F", text="Physical"),
            ],
            label="Select Streaming Type"
        )

        def carregar_livros():
            """
            Fetch and display the list of books from the API.
            """
            lista_livros.controls.clear()
            for i in get_livros():
                lista_livros.controls.append(
                    ft.Container(
                        ft.Text(i['nome']),
                        bgcolor=ft.colors.BLACK12,
                        padding=15,
                        alignment=ft.alignment.center,
                        margin=3,
                        border_radius=10,
                        on_click=lambda e, livro_id=i['id']: page.go(f"/review?id={livro_id}")
                    )
                )
            page.update()

        def cadastrar(e):
            """
            Register a new book using the API.
            """
            data = {
                'nome': nome_input.value,
                'streaming': streaming_select.value,
            }
            response = requests.post('http://127.0.0.1:8000/api/livros/', json=data)
            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("Book registered successfully!"))
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Failed to register book."))
            page.snack_bar.open = True
            carregar_livros()

        cadastrar_btn = ft.ElevatedButton("Register", on_click=cadastrar)

        lista_livros = ft.ListView()

        carregar_livros()

        page.views.append(
            ft.View(
                "/",
                controls=[
                    nome_input,
                    streaming_select,
                    cadastrar_btn,
                    lista_livros
                ]
            )
        )

    def review_page(livro_id):
        """
        Review page for managing a book's details.
        
        Args:
        - livro_id (int): The ID of the book to review.
        """
        nota_input = ft.TextField(label="Rating (integer)", text_align=ft.TextAlign.LEFT, value="0", width=100)
        comentario_input = ft.TextField(label="Comment", multiline=True, expand=True)

        def avaliar(e):
            """
            Submit a review for the book using the API.
            """
            data = {
                'nota': int(nota_input.value),
                'comentarios': comentario_input.value
            }

            try:
                response = requests.put(f'http://127.0.0.1:8000/api/livros/{livro_id}', json=data)

                if response.status_code == 200:
                    page.snack_bar = ft.SnackBar(ft.Text("Review submitted successfully!"))
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Error submitting review."))
                page.snack_bar.open = True

            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Connection error: {ex}"))
                page.snack_bar.open = True

            page.update()

        def deletar(e):
            """
            Delete the book using the API.
            """
            try:
                response = requests.delete(f'http://127.0.0.1:8000/api/livros/{livro_id}')
                if response.status_code == 200:
                    page.snack_bar = ft.SnackBar(ft.Text("Book deleted successfully!"))
                    page.go("/")  # Return to home page after deletion
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Error deleting book."))
                page.snack_bar.open = True

            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Connection error: {ex}"))
                page.snack_bar.open = True

            page.update()

        avaliar_btn = ft.ElevatedButton("Submit Review", on_click=avaliar)
        deletar_btn = ft.ElevatedButton("Delete Book", on_click=deletar)
        voltar_btn = ft.ElevatedButton("Back", on_click=lambda _: page.go('/'))

        page.views.append(
            ft.View(
                "/review",
                controls=[
                    nota_input,
                    comentario_input,
                    avaliar_btn,
                    deletar_btn,
                    voltar_btn
                ]
            )
        )

    def route_change(e):
        """
        Handle route changes and update the page view accordingly.
        """
        page.views.clear()

        if page.route == "/":
            home_page()
        elif page.route.startswith("/review"):
            parsed_url = urlparse(page.route)
            query_params = parse_qs(parsed_url.query)
            livro_id = query_params.get('id')[0]
            review_page(livro_id)

        page.update()

    page.on_route_change = route_change
    page.go('/')


ft.app(target=main)
