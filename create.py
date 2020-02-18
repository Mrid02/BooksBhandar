import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))

db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("CREATE TABLE books(id SERIAL PRIMARY KEY, isbn VARCHAR UNIQUE NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year SMALLINT NOT NULL)")
    db.execute("CREATE TABLE users(id SERIAL PRIMARY KEY, username VARCHAR UNIQUE NOT NULL, password VARCHAR NOT NULL)")
    db.execute("CREATE TABLE reviews(id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users, book_id INTEGER REFERENCES books, rating SMALLINT NOT NULL, review VARCHAR NOT NULL)")
    
    db.commit()

    print ("Created books, users and reviews table")


if __name__ == "__main__":
    main()

    