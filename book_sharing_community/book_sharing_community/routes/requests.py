from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, Book, BorrowRequest

requests_bp = Blueprint('requests', __name__)

@requests_bp.route('/requests')
@login_required
def my_requests():
    # Incoming requests: books owned by current user requested by others
    incoming = BorrowRequest.query.filter_by(owner_id=current_user.id).order_by(BorrowRequest.request_date.desc()).all()
    
    # Outgoing requests: books requested by current user from others
    outgoing = BorrowRequest.query.filter_by(borrower_id=current_user.id).order_by(BorrowRequest.request_date.desc()).all()

    return render_template('my_requests.html', incoming=incoming, outgoing=outgoing)


@requests_bp.route('/requests/new/<int:book_id>', methods=['POST'])
@login_required
def create_request(book_id):
    book = Book.query.get_or_404(book_id)

    # Cannot borrow own book
    if book.owner_id == current_user.id:
        flash('You cannot request to borrow your own book!', 'warning')
        return redirect(url_for('books.detail', book_id=book.id))

    # Cannot borrow unavailable book
    if not book.is_available:
        flash('This book is currently checked out by someone else.', 'warning')
        return redirect(url_for('books.detail', book_id=book.id))

    # Check for duplicate pending request
    pending = BorrowRequest.query.filter_by(
        book_id=book.id,
        borrower_id=current_user.id,
        status='Pending'
    ).first()
    if pending:
        flash('You already have a pending request for this book.', 'info')
        return redirect(url_for('books.detail', book_id=book.id))

    duration = request.form.get('duration_days', type=int) or 14
    message = request.form.get('message', '').strip()

    new_request = BorrowRequest(
        book_id=book.id,
        borrower_id=current_user.id,
        owner_id=book.owner_id,
        duration_days=duration,
        message=message,
        status='Pending',
        request_date=datetime.utcnow()
    )

    db.session.add(new_request)
    db.session.commit()

    flash(f'Borrow request for "{book.title}" sent to {book.owner.full_name}!', 'success')
    return redirect(url_for('requests.my_requests'))


@requests_bp.route('/requests/<int:request_id>/approve', methods=['POST'])
@login_required
def approve_request(request_id):
    req = BorrowRequest.query.get_or_404(request_id)

    if req.owner_id != current_user.id:
        abort(403)

    if req.status != 'Pending':
        flash('This request has already been processed.', 'info')
        return redirect(url_for('requests.my_requests'))

    req.status = 'Approved'
    req.action_date = datetime.utcnow()
    
    # Mark book as borrowed/unavailable
    req.book.is_available = False

    # Decline any other pending requests for the same book
    other_pending = BorrowRequest.query.filter(
        BorrowRequest.book_id == req.book_id,
        BorrowRequest.id != req.id,
        BorrowRequest.status == 'Pending'
    ).all()
    for other in other_pending:
        other.status = 'Declined'
        other.action_date = datetime.utcnow()

    db.session.commit()
    flash(f'You approved {req.borrower.full_name}\'s request for "{req.book.title}".', 'success')
    return redirect(url_for('requests.my_requests'))


@requests_bp.route('/requests/<int:request_id>/decline', methods=['POST'])
@login_required
def decline_request(request_id):
    req = BorrowRequest.query.get_or_404(request_id)

    if req.owner_id != current_user.id:
        abort(403)

    if req.status != 'Pending':
        flash('This request has already been processed.', 'info')
        return redirect(url_for('requests.my_requests'))

    req.status = 'Declined'
    req.action_date = datetime.utcnow()
    db.session.commit()

    flash(f'Request declined for "{req.book.title}".', 'info')
    return redirect(url_for('requests.my_requests'))


@requests_bp.route('/requests/<int:request_id>/return', methods=['POST'])
@login_required
def return_book(request_id):
    req = BorrowRequest.query.get_or_404(request_id)

    # Either owner or borrower can mark as returned
    if req.owner_id != current_user.id and req.borrower_id != current_user.id:
        abort(403)

    if req.status != 'Approved':
        flash('Only approved borrowed books can be marked as returned.', 'warning')
        return redirect(url_for('requests.my_requests'))

    req.status = 'Returned'
    req.return_date = datetime.utcnow()
    
    # Restore book availability
    req.book.is_available = True
    db.session.commit()

    flash(f'"{req.book.title}" has been marked as returned and is now available in the community library again!', 'success')
    return redirect(url_for('requests.my_requests'))


@requests_bp.route('/requests/<int:request_id>/cancel', methods=['POST'])
@login_required
def cancel_request(request_id):
    req = BorrowRequest.query.get_or_404(request_id)

    if req.borrower_id != current_user.id:
        abort(403)

    if req.status != 'Pending':
        flash('You can only cancel pending requests.', 'warning')
        return redirect(url_for('requests.my_requests'))

    db.session.delete(req)
    db.session.commit()

    flash(f'Your request for "{req.book.title}" has been cancelled.', 'info')
    return redirect(url_for('requests.my_requests'))
