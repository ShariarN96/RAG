import os

from pydantic import BaseModel, Field

from src.etl.crossref import print_results

current_dir = os.path.dirname(__file__)


class ArticleMetadata(BaseModel):
    doi: str = Field(description="Digital Object Identifier of the article")

    title: str = Field(description="Title of the article")

    url: str = Field(description="URL of the article")

    container_title: str = Field(description="Container title (e.g., journal name)")

    publication_date: str = Field(description="Publication date in YYYY-MM-DD format")


print_results()
