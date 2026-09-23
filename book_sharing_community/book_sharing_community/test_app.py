"""
Automated Test Suite for Book Sharing Community Mini-Project.
Runs end-to-end tests across authentication, book management, borrowing workflow, and reviews.
"""

import unittest
from app import create_app
from models import db, User, Book, BorrowRequest, Review

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

class BookCommunityTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register(self, username, email, password, full_name, location='Campus'):
        return self.client.post('/register', data={
            'username': username,
            'email': email,
            'password': password,
            'confirm_password': password,
            'full_name': full_name,
            'phone': '1234567890',
            'location': location
        }, follow_redirects=True)

    def login(self, username_or_email, password):
        return self.client.post('/login', data={
            'username_or_email': username_or_email,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_user_registration_and_login(self):
        response = self.register('testuser', 'test@test.com', 'password123', 'Test User')
        self.assertIn(b'Registration successful', response.data)

        # Duplicate check
        dup = self.register('testuser', 'another@test.com', 'password123', 'Duplicate User')
        self.assertIn(b'Username is already taken', dup.data)

        # Login
        log_res = self.login('testuser', 'password123')
        self.assertIn(b'Welcome back, Test User', log_res.data)

    def test_book_crud(self):
        self.register('owner1', 'owner1@test.com', 'pass123', 'Owner One')
        self.login('owner1', 'pass123')

        # Add book
        add_res = self.client.post('/books/add', data={
            'title': 'Test Python Book',
            'author': 'Guido van Rossum',
            'genre': 'Computer Science & Tech',
            'condition': 'Like New',
            'isbn': '1234567890',
            'description': 'A great book about Python.',
            'cover_url': ''
        }, follow_redirects=True)
        self.assertIn(b'has been listed in the community library', add_res.data)

        book = Book.query.filter_by(title='Test Python Book').first()
        self.assertIsNotNone(book)
        self.assertTrue(book.is_available)

        # Edit book
        edit_res = self.client.post(f'/books/{book.id}/edit', data={
            'title': 'Test Python Book 2nd Ed',
            'author': 'Guido van Rossum',
            'genre': 'Computer Science & Tech',
            'condition': 'Good',
            'isbn': '1234567890',
            'description': 'Updated edition.',
            'cover_url': ''
        }, follow_redirects=True)
        self.assertIn(b'Book details updated successfully', edit_res.data)
        self.assertEqual(book.title, 'Test Python Book 2nd Ed')

    def test_borrowing_workflow(self):
        # Setup Owner
        self.register('owner', 'owner@test.com', 'pass123', 'Owner Name')
        self.login('owner', 'pass123')
        self.client.post('/books/add', data={
            'title': 'Algorithms Book',
            'author': 'CLRS',
            'genre': 'Computer Science & Tech',
            'condition': 'Good',
            'description': 'Standard algorithms book.'
        }, follow_redirects=True)
        self.logout()

        book = Book.query.filter_by(title='Algorithms Book').first()

        # Setup Borrower
        self.register('borrower', 'borrower@test.com', 'pass123', 'Borrower Name')
        self.login('borrower', 'pass123')

        # Send Borrow Request
        req_res = self.client.post(f'/requests/new/{book.id}', data={
            'duration_days': 14,
            'message': 'Need this for preparation'
        }, follow_redirects=True)
        self.assertIn(b'Algorithms Book', req_res.data)
        self.assertIn(b'sent to Owner Name', req_res.data)

        req = BorrowRequest.query.filter_by(book_id=book.id).first()
        self.assertEqual(req.status, 'Pending')
        self.logout()

        # Owner logs in to Approve
        self.login('owner', 'pass123')
        appr_res = self.client.post(f'/requests/{req.id}/approve', follow_redirects=True)
        self.assertIn(b'You approved', appr_res.data)

        # Book should now be marked unavailable
        db.session.refresh(book)
        self.assertFalse(book.is_available)

        # Mark as returned
        ret_res = self.client.post(f'/requests/{req.id}/return', follow_redirects=True)
        self.assertIn(b'marked as returned and is now available', ret_res.data)

        # Book should now be available again
        db.session.refresh(book)
        self.assertTrue(book.is_available)

    def test_reviews_and_ratings(self):
        self.register('owner', 'owner@test.com', 'pass123', 'Owner')
        self.login('owner', 'pass123')
        self.client.post('/books/add', data={
            'title': 'Reviewable Book',
            'author': 'Author',
            'genre': 'Fiction'
        }, follow_redirects=True)
        self.logout()

        book = Book.query.filter_by(title='Reviewable Book').first()

        # Reviewer
        self.register('reviewer', 'rev@test.com', 'pass123', 'Reviewer')
        self.login('reviewer', 'pass123')

        rev_res = self.client.post(f'/books/{book.id}/review', data={
            'rating': 5,
            'comment': 'Awesome read!'
        }, follow_redirects=True)
        self.assertIn(b'Thank you! Your review has been posted', rev_res.data)

        db.session.refresh(book)
        self.assertEqual(book.average_rating, 5.0)
        self.assertEqual(book.review_count, 1)

if __name__ == '__main__':
    unittest.main()
