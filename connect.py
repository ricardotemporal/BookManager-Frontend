"""
This module provides utility functions to interact with the book API.

Functions:
- get_livros: Fetches the list of books from the API.
"""

import requests

def get_livros():
    """
    Fetch the list of books from the API.

    Returns:
    - A JSON response containing the list of books.
    """
    response = requests.get('http://127.0.0.1:8000/api/livros')
    return response.json()
