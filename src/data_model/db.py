import os
import sqlite3
from typing import List

from pydantic import BaseModel, Field
from src.etl.crossref import wiley_dois_2025_by_keyword

current_dir = os.path.dirname(__file__)
DB_PATH = os.path.join(current_dir, "articles_metadata.db")


class ArticleMetadata(BaseModel):
    doi: str = Field(description="Digital Object Identifier of the article")

    title: str = Field(description="Title of the article")

    url: str = Field(description="URL of the article")

    container_title: str = Field(description="Container title (e.g., journal name)")

    publication_date: str = Field(description="Publication date in YYYY-MM-DD format")

    @classmethod
    def fetch_and_create_articles(
        cls, query: str, limit: int = 5
    ) -> List["ArticleMetadata"]:
        """Fetch articles from Wiley and create ArticleMetadata instances."""
        articles_data = wiley_dois_2025_by_keyword(query, limit=limit)
        new_articles = []

        for article in articles_data:
            try:
                article_metadata = cls(
                    doi=article["DOI"],
                    title=article["title"][0],
                    url=article["URL"],
                    container_title=article["container-title"][0],
                    publication_date=article["created"]["date-time"][:10],
                )
                new_articles.append(article_metadata)
            except (KeyError, IndexError) as e:
                print(f"Error processing article: {e}")
                continue

        return new_articles


# --- SQLite Helper Functions ---
def create_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            doi TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            container_title TEXT,
            publication_date TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def insert_article(article: ArticleMetadata):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        INSERT OR IGNORE INTO articles (doi, title, url, container_title, publication_date)
        VALUES (?, ?, ?, ?, ?)
    """,
        (
            article.doi,
            article.title,
            article.url,
            article.container_title,
            article.publication_date,
        ),
    )
    conn.commit()
    conn.close()


def get_all_articles() -> List[ArticleMetadata]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT doi, title, url, container_title, publication_date FROM articles")
    rows = c.fetchall()
    conn.close()
    return [
        ArticleMetadata(
            doi=row[0],
            title=row[1],
            url=row[2],
            container_title=row[3],
            publication_date=row[4],
        )
        for row in rows
    ]


def search_by_title(search_term: str) -> List[ArticleMetadata]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT doi, title, url, container_title, publication_date
        FROM articles
        WHERE LOWER(title) LIKE ?
    """,
        (f"%{search_term.lower()}%",),
    )
    rows = c.fetchall()
    conn.close()
    return [
        ArticleMetadata(
            doi=row[0],
            title=row[1],
            url=row[2],
            container_title=row[3],
            publication_date=row[4],
        )
        for row in rows
    ]


def filter_by_date(
    start_date: str = None, end_date: str = None
) -> List[ArticleMetadata]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = "SELECT doi, title, url, container_title, publication_date FROM articles WHERE 1=1"
    params = []
    if start_date:
        query += " AND publication_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND publication_date <= ?"
        params.append(end_date)
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [
        ArticleMetadata(
            doi=row[0],
            title=row[1],
            url=row[2],
            container_title=row[3],
            publication_date=row[4],
        )
        for row in rows
    ]


# --- Example usage ---
if __name__ == "__main__":
    create_table()
    # Fetch new articles
    query = "high-entropy alloy"
    new_articles = ArticleMetadata.fetch_and_create_articles(query, limit=5)
    print(f"Added {len(new_articles)} new articles")
    # Insert new articles into SQLite
    for article in new_articles:
        insert_article(article)
    # Retrieve and display all articles from SQLite
    all_articles = get_all_articles()
    print(f"Total articles in SQLite DB: {len(all_articles)}")
    for article in all_articles:
        print(f"- {article.title} ({article.publication_date})")
    # Example: search by title
    alloy_articles = search_by_title("alloy")
    print(f"\nArticles with 'alloy' in the title: {len(alloy_articles)}")
    for article in alloy_articles:
        print(f"- {article.title}")
    # Example: filter by date
    recent_articles = filter_by_date(start_date="2025-01-01")
    print(f"\nArticles published since 2025: {len(recent_articles)}")
    for article in recent_articles:
        print(f"- {article.title} ({article.publication_date})")
