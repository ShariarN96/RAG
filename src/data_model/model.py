import json
import os
from typing import ClassVar, Dict, List

from pydantic import BaseModel, Field

from RAG.src.etl.crossref import wiley_dois_2025_by_keyword

current_dir = os.path.dirname(__file__)
MASTER_DATA_FILE = os.path.join(current_dir, "master_articles.json")


class ArticleMetadata(BaseModel):
    doi: str = Field(description="Digital Object Identifier of the article")

    title: str = Field(description="Title of the article")

    url: str = Field(description="URL of the article")

    container_title: str = Field(description="Container title (e.g., journal name)")

    publication_date: str = Field(description="Publication date in YYYY-MM-DD format")

    _master_articles: ClassVar[Dict[str, "ArticleMetadata"]] = {}

    @classmethod
    def load_master_data(cls) -> None:
        """Load previously saved articles from the master data file."""
        if os.path.exists(MASTER_DATA_FILE):
            with open(MASTER_DATA_FILE, "r") as f:
                data = json.load(f)
                cls._master_articles = {
                    doi: cls(**article_data) for doi, article_data in data.items()
                }

    @classmethod
    def save_master_data(cls) -> None:
        """Save all articles to the master data file."""
        data = {
            doi: article.model_dump() for doi, article in cls._master_articles.items()
        }
        with open(MASTER_DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

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
                # Only add if not already in master list
                if article_metadata.doi not in cls._master_articles:
                    cls._master_articles[article_metadata.doi] = article_metadata
                    new_articles.append(article_metadata)
            except (KeyError, IndexError) as e:
                print(f"Error processing article: {e}")
                continue

        # Save updated master data
        cls.save_master_data()
        return new_articles

    @classmethod
    def get_all_articles(cls) -> List["ArticleMetadata"]:
        """Get all articles from the master list."""
        return list(cls._master_articles.values())


ArticleMetadata.load_master_data()


query = "high-entropy alloy"
articles = wiley_dois_2025_by_keyword(query, limit=10)


def create_article_metadata(articles):
    article_metadata_list = []
    for article in articles:
        doi = article["DOI"]
        title = article["title"][0]
        url = article["URL"]
        container_title = article["container-title"][0]
        publication_date = article["created"]["date-time"][0:10]

        article_metadata = ArticleMetadata(
            doi=doi,
            title=title,
            url=url,
            container_title=container_title,
            publication_date=publication_date,
        )
        article_metadata_list.append(article_metadata)
    return article_metadata_list


query = "high-entropy alloy"
new_articles = ArticleMetadata.fetch_and_create_articles(query, limit=5)


if __name__ == "__main__":
    # Fetch new articles
    query = "high-entropy alloy"
    new_articles = ArticleMetadata.fetch_and_create_articles(query, limit=5)

    print(f"Added {len(new_articles)} new articles")
    print(f"Total articles in master list: {len(ArticleMetadata.get_all_articles())}")

    # Access all articles
    all_articles = ArticleMetadata.get_all_articles()
    for article in all_articles:
        print(f"\nTitle: {article.title}")
        print(f"DOI: {article.doi}")
        print(f"Journal: {article.container_title}")
