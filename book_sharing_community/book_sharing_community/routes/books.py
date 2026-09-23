from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, Book, Review, BorrowRequest

books_bp = Blueprint('books', __name__)

GENRES = [
    'Fiction', 'Non-Fiction', 'Computer Science & Tech', 'Engineering & Math',
    'Literature & Classics', 'Science Fiction & Fantasy', 'Self-Help & Productivity',
    'History & Politics', 'Business & Economics', 'Philosophy & Psychology'
]

CONDITIONS = ['Like New', 'Good', 'Fair']

@books_bp.route('/books')
def catalog():
    query = request.args.get('q', '').strip()
    selected_genre = request.args.get('genre', '').strip()
    selected_condition = request.args.get('condition', '').strip()
    availability = request.args.get('availability', 'all')

    books_query = Book.query

    if query:
        search_filter = f"%{query}%"
        books_query = books_query.filter(
            (Book.title.ilike(search_filter)) | 
            (Book.author.ilike(search_filter)) | 
            (Book.description.ilike(search_filter))
        )

    if selected_genre and selected_genre != 'all':
        books_query = books_query.filter_by(genre=selected_genre)

    if selected_condition and selected_condition != 'all':
        books_query = books_query.filter_by(condition=selected_condition)

    if availability == 'available':
        books_query = books_query.filter_by(is_available=True)
    elif availability == 'borrowed':
        books_query = books_query.filter_by(is_available=False)

    books = books_query.order_by(Book.created_at.desc()).all()

    return render_template(
        'catalog.html',
        books=books,
        genres=GENRES,
        conditions=CONDITIONS,
        current_query=query,
        current_genre=selected_genre,
        current_condition=selected_condition,
        current_availability=availability
    )


@books_bp.route('/books/<int:book_id>')
def detail(book_id):
    book = Book.query.get_or_404(book_id)
    reviews = book.reviews.all()
    user_review = None
    existing_request = None

    if current_user.is_authenticated:
        user_review = Review.query.filter_by(book_id=book.id, user_id=current_user.id).first()
        existing_request = BorrowRequest.query.filter_by(
            book_id=book.id, 
            borrower_id=current_user.id,
            status='Pending'
        ).first()

    return render_template(
        'book_detail.html',
        book=book,
        reviews=reviews,
        user_review=user_review,
        existing_request=existing_request
    )


@books_bp.route('/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        genre = request.form.get('genre', '').strip()
        isbn = request.form.get('isbn', '').strip()
        condition = request.form.get('condition', 'Good')
        description = request.form.get('description', '').strip()
        cover_url = request.form.get('cover_url', '').strip()

        if not title or not author or not genre:
            flash('Title, Author, and Genre are required.', 'danger')
            return render_template('add_book.html', genres=GENRES, conditions=CONDITIONS)

        # Fallback default cover if none provided
        if not cover_url:
            cover_url = "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80"

        new_book = Book(
            title=title,
            author=author,
            genre=genre,
            isbn=isbn,
            condition=condition,
            description=description,
            cover_url=cover_url,
            owner_id=current_user.id,
            is_available=True
        )

        db.session.add(new_book)
        db.session.commit()

        flash(f'"{title}" has been listed in the community library!', 'success')
        return redirect(url_for('books.detail', book_id=new_book.id))

    return render_template('add_book.html', genres=GENRES, conditions=CONDITIONS)


@books_bp.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)

    if book.owner_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        book.title = request.form.get('title', '').strip()
        book.author = request.form.get('author', '').strip()
        book.genre = request.form.get('genre', '').strip()
        book.isbn = request.form.get('isbn', '').strip()
        book.condition = request.form.get('condition', 'Good')
        book.description = request.form.get('description', '').strip()
        book.cover_url = request.form.get('cover_url', '').strip() or book.cover_url

        db.session.commit()
        flash('Book details updated successfully!', 'success')
        return redirect(url_for('books.detail', book_id=book.id))

    return render_template('edit_book.html', book=book, genres=GENRES, conditions=CONDITIONS)


@books_bp.route('/books/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    if book.owner_id != current_user.id:
        abort(403)

    db.session.delete(book)
    db.session.commit()
    flash(f'"{book.title}" was removed from your shared books.', 'info')
    return redirect(url_for('auth.profile'))


@books_bp.route('/books/<int:book_id>/review', methods=['POST'])
@login_required
def submit_review(book_id):
    book = Book.query.get_or_404(book_id)
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()

    if not rating or rating < 1 or rating > 5:
        flash('Please select a rating between 1 and 5 stars.', 'warning')
        return redirect(url_for('books.detail', book_id=book.id))

    if not comment:
        flash('Please provide a short review comment.', 'warning')
        return redirect(url_for('books.detail', book_id=book.id))

    # Check if user already reviewed
    existing = Review.query.filter_by(book_id=book.id, user_id=current_user.id).first()
    if existing:
        existing.rating = rating
        existing.comment = comment
        flash('Your review has been updated!', 'success')
    else:
        new_review = Review(
            book_id=book.id,
            user_id=current_user.id,
            rating=rating,
            comment=comment
        )
        db.session.add(new_review)
        flash('Thank you! Your review has been posted.', 'success')

    db.session.commit()
    return redirect(url_for('books.detail', book_id=book.id))
