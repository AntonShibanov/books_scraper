import time
import requests
import schedule
from bs4 import BeautifulSoup


def get_book_data(book_url: str) -> dict:
    """
    Извлекает данные о книге с указанной страницы.

    Args:
        book_url (str): URL страницы книги

    Return:
        dict: Словарь с данными о книге:
            - title: название
            - price: цена
            - rating: рейтинг
            - stock: наличие
            - description: описание
            - product_info: таблица характеристик
    """
    try:
        response = requests.get(book_url)
        soup = BeautifulSoup(response.content, "html.parser")

        title = soup.find("h1").text
        price = soup.find("p", class_="price_color").text
        rating = soup.find("p", class_="star-rating")["class"][1]
        stock = soup.find("p", class_="instock availability").text.strip()
        description = soup.find("meta", attrs={"name": "description"})[
            "content"
        ].strip()

        product_info = {}
        info_table = soup.find("table", class_="table table-striped")
        for row in info_table.find_all("tr"):
            header = row.find("th").text
            value = row.find("td").text
            product_info[header] = value

        return {
            "title": title,
            "price": price,
            "rating": rating,
            "stock": stock,
            "description": description,
            "product_info": product_info,
        }
    except (requests.RequestException, AttributeError, KeyError) as e:
        print(f"Ошибка при получении данных с {book_url}: {e}")
        return None


def scrape_books(is_save: bool = False) -> list:
    """
    Собирает данные о всех книгах со всех страниц каталога.

    Args:
        is_save (bool): Флаг сохранения результатов в файл

    Return:
        list: Список словарей с данными о книгах
    """
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    all_books = []

    for page in range(1, 51):
        try:
            url = base_url.format(page)
            response = requests.get(url)

            soup = BeautifulSoup(response.content, "html.parser")
            books = soup.find_all("article", class_="product_pod")

            for book in books:
                relative_link = book.find("h3").find("a")["href"]
                if relative_link.startswith("../../../"):
                    book_url = relative_link.replace(
                        "../../../", "http://books.toscrape.com/catalogue/"
                    )
                elif relative_link.startswith("../../"):
                    book_url = relative_link.replace(
                        "../../", "http://books.toscrape.com/"
                    )
                else:
                    book_url = f"http://books.toscrape.com/catalogue/{relative_link}"
                book_data = get_book_data(book_url)
                all_books.append(book_data)
                print(f"Получаем данные из: {book_url}")
                time.sleep(0.5)  # Чтобы не перегружать сервер

        except requests.RequestException as e:
            print(f"Ошибка при загрузке страницы {page}: {e}")
            continue

    if is_save:
        with open("books_data.txt", "w", encoding="utf-8") as f:
            for book in all_books:
                f.write(str(book) + "\n")

    return all_books


def scheduled_parcing() -> None:
    """Функция для регулярной выгрузки в 19:00"""
    scrape_books(is_save=True)
    print("Данные обновлены в", time.strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    schedule.every().day.at("19:00").do(scheduled_parcing)

    print("Ожидание выполнения в 19:00")
    while True:
        schedule.run_pending()
        time.sleep(30)
