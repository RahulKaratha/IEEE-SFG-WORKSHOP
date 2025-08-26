from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

books = [
    {"id": 1, "title": "The Hobbit", "author": "J.R.R. Tolkien"},
    {"id": 2, "title": "1984", "author": "George Orwell"}
]

class Book(BaseModel):
    title: str
    author: str

# GET – Retrieve all books
@app.get("/books")
def get_books():
    return books

# POST – Add a new book
@app.post("/books")
def add_book(book: Book):
    new_book = {"id": len(books) + 1, "title": book.title, "author": book.author}
    books.append(new_book)
    return {"message": "Book added", "book": new_book}

# PUT – Update a book by ID
@app.put("/books/{book_id}")
def update_book(book_id: int, updated_book: Book):
    for book in books:
        if book["id"] == book_id:
            book["title"] = updated_book.title
            book["author"] = updated_book.author
            return {"message": "Book updated", "book": book}
    raise HTTPException(status_code=404, detail="Book not found")

# DELETE – Delete a book by ID
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return {"message": "Book deleted"}
    raise HTTPException(status_code=404, detail="Book not found")
