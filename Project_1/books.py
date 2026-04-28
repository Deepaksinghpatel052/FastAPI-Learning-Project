from fastapi import Body, FastAPI

app = FastAPI()


BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/{book_title}")
async def read_one_books(book_title: str):
    for book in BOOKS:
        if book.get("title").casefold() == book_title.casefold():
            return book

@app.get("/books/")
async def read_one_book_with_query(categoryes: str):
    cate_books = []
    for book in BOOKS:
        if book.get("category").casefold() == categoryes.casefold():
            cate_books.append(book)
    return cate_books

@app.get("/author-books/{author}")
async def read_one_book_with_query_and_dinamic(author:str, categoryes: str = None):
    cate_books = []
    for book in BOOKS:
        if book.get("author").casefold() == author.casefold():
            if categoryes != None:
                if book.get("category").casefold() == categoryes.casefold():
                    cate_books.append(book)
            else:
                cate_books.append(book)
    return cate_books


@app.post("/books/create_new_books")
async def create_new_book(new_book=Body()):
    BOOKS.append(new_book)

@app.put("/books/update_book")
async def update_book(update_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == update_book.get("title").casefold():
            BOOKS[i] = update_book


@app.delete("/books/delete_book/{book_title}")
async def update_book(book_title : str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == book_title.casefold():
            BOOKS.pop(i)
            break

@app.get("/books/get_all_book_by_author/{author}")
async def get_all_book_by_autor(author: str):
    all_books_of_author = []
    for book in BOOKS:
        if book.get("author").casefold() == author.casefold():
            all_books_of_author.append(book)
    return all_books_of_author