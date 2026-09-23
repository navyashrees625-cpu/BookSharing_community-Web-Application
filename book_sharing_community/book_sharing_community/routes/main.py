from flask import Blueprint, render_template
from sqlalchemy import func
from models import db, User, Book, BorrowRequest, Review

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured_books = Book.query.filter_by(is_available=True).order_by(Book.created_at.desc()).limit(8).all()
    total_books = Book.query.count()
    total_users = User.query.count()
    total_exchanges = BorrowRequest.query.filter(BorrowRequest.status.in_(['Approved', 'Returned'])).count()

    return render_template(
        'index.html',
        featured_books=featured_books,
        total_books=total_books,
        total_users=total_users,
        total_exchanges=total_exchanges
    )


@main_bp.route('/stats')
def stats():
    total_users = User.query.count()
    total_books = Book.query.count()
    available_books = Book.query.filter_by(is_available=True).count()
    borrowed_books = Book.query.filter_by(is_available=False).count()
    total_requests = BorrowRequest.query.count()
    completed_returns = BorrowRequest.query.filter_by(status='Returned').count()
    active_borrows = BorrowRequest.query.filter_by(status='Approved').count()
    total_reviews = Review.query.count()

    # Genre breakdown
    genre_counts = db.session.query(Book.genre, func.count(Book.id)).group_by(Book.genre).all()

    return render_template(
        'stats.html',
        total_users=total_users,
        total_books=total_books,
        available_books=available_books,
        borrowed_books=borrowed_books,
        total_requests=total_requests,
        completed_returns=completed_returns,
        active_borrows=active_borrows,
        total_reviews=total_reviews,
        genre_counts=genre_counts
    )


@main_bp.route('/about')
def about():
    return render_template('about.html')
