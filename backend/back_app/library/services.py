import datetime
import requests
from bs4 import BeautifulSoup
from library.models import Book, Category

def scrape_book_info(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except Exception as e:
        raise Exception(f"Error querying URL: {str(e)}")
    
    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.find("h1")
    meta_description = soup.find("meta", attrs={"name": "description"})
    scraped_title = title_tag.text.strip() if title_tag else "Unknown"
    scraped_description = (
        meta_description.get("content", "").strip()
        if meta_description and meta_description.get("content")
        else ""
    )

    default_category, _ = Category.objects.get_or_create(name="Scraped")
    book, created = Book.objects.update_or_create(
        title=scraped_title,
        category=default_category,
        defaults={
            "author": "Unknown",
            "publication_date": datetime.date.today(),
            "description": scraped_description,
        },
    )
    return book, created
