from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(120), nullable=True)  # e.g., Campus block, neighborhood
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    books = db.relationship('Book', back_populates='owner', cascade='all, delete-orphan', lazy='dynamic')
    sent_requests = db.relationship(
        'BorrowRequest', 
        foreign_keys='BorrowRequest.borrower_id', 
        back_populates='borrower', 
        cascade='all, delete-orphan', 
        lazy='dynamic'
    )
    received_requests = db.relationship(
        'BorrowRequest', 
        foreign_keys='BorrowRequest.owner_id', 
        back_populates='owner', 
        cascade='all, delete-orphan', 
        lazy='dynamic'
    )
    reviews = db.relationship('Review', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False, index=True)
    genre = db.Column(db.String(50), nullable=False, index=True)
    isbn = db.Column(db.String(30), nullable=True)
    condition = db.Column(db.String(30), default='Good')  # Like New, Good, Fair
    description = db.Column(db.Text, nullable=True)
    cover_url = db.Column(db.String(500), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    owner = db.relationship('User', back_populates='books')
    requests = db.relationship('BorrowRequest', back_populates='book', cascade='all, delete-orphan', lazy='dynamic')
    reviews = db.relationship('Review', back_populates='book', cascade='all, delete-orphan', lazy='dynamic', order_by='desc(Review.created_at)')

    @property
    def average_rating(self):
        revs = self.reviews.all()
        if not revs:
            return 0.0
        return round(sum(r.rating for r in revs) / len(revs), 1)

    @property
    def review_count(self):
        return self.reviews.count()

    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'


class BorrowRequest(db.Model):
    __tablename__ = 'borrow_requests'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    duration_days = db.Column(db.Integer, default=14)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Declined, Returned
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    action_date = db.Column(db.DateTime, nullable=True)
    return_date = db.Column(db.DateTime, nullable=True)

    # Relationships
    book = db.relationship('Book', back_populates='requests')
    borrower = db.relationship('User', foreign_keys=[borrower_id], back_populates='sent_requests')
    owner = db.relationship('User', foreign_keys=[owner_id], back_populates='received_requests')

    def __repr__(self):
        return f'<BorrowRequest Book:{self.book_id} Borrower:{self.borrower_id} Status:{self.status}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    book = db.relationship('Book', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

    def __repr__(self):
        return f'<Review Book:{self.book_id} Rating:{self.rating}>'
