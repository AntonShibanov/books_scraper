import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import get_book_data, scrape_books


def test_get_book_data_structure() -> None:
    """Тест проверяет структуру возвращаемых данных"""
    url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    data = get_book_data(url)

    assert isinstance(data, dict)
    expected_keys = ["title", "price", "rating", "stock", "description", "product_info"]
    assert all(key in data for key in expected_keys)


def test_scrape_books_count() -> None:
    """Тест проверяет количество собранных книг"""
    books = scrape_books(is_save=False)
    assert len(books) > 0
    assert isinstance(books, list)


def test_book_data_content() -> None:
    """Тест проверяет корректность данных конкретной книги"""
    url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    data = get_book_data(url)

    assert data["title"] == "A Light in the Attic"
    assert "£" in data["price"]
    assert data["rating"] in ["One", "Two", "Three", "Four", "Five"]
