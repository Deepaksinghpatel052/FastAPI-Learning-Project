from typing import Optional

from fastapi import FastAPI, Body, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(description="id is not required on creation", default=None)
    title: str = Field(min_length=2)
    author: str = Field(min_length=2)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt= -1, lt=6)
    published_date: int = Field(gt=1990, lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new Book",
                "author": "Book authon",
                "description": "Book description",
                "rating": 5,
                "published_date": 2012
            }
        }
    }


BOOKS = [
    Book(1, 'Computer Science Pro', 'codingwithroby', 'A very nice book!', 5, 2010),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 5, 2012),
    Book(3, 'Master Endpoints', 'codingwithroby', 'A awesome book!', 5, 1996),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2, 2020),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3, 2020),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1, 2026)
]

@app.get("/books/get_all_books", status_code=status.HTTP_200_OK)
async def get_all_books():
    return BOOKS

@app.get("/books/rating", status_code=status.HTTP_200_OK)
async def get_books_by_rating(book_rating: int = Query(gt= -1, lt=6)):
    rating_books = []
    for book in BOOKS:
        if book.rating == book_rating:
            rating_books.append(book)
    if rating_books:
        return rating_books
    else:
        raise HTTPException(status_code=404, detail="Tiem not found")



@app.get("/book/{book_id}", status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: int = Path(gt = 0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise  HTTPException(status_code=404, detail="Item not found")

@app.post("/books/create_new_book", status_code=status.HTTP_201_CREATED)
async def create_new_book(bookRequest: BookRequest):
    new_book = Book(**bookRequest.model_dump())
    BOOKS.append(file_book_id(new_book))


def file_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def book_update(Book: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == Book.id:
            BOOKS[i] = Book
            break
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/books/dlete_books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt = 0)):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            break
    else:
        raise HTTPException(status_code=404, detail="Item not found")