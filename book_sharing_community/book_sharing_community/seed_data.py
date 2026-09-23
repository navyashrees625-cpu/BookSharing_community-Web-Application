"""
Database Seeder Script for Book Sharing Community.
Populates realistic demo users, books across various categories, reviews, and borrow requests.
Run with: python seed_data.py
"""

from datetime import datetime, timedelta
from app import create_app
from models import db, User, Book, BorrowRequest, Review

app = create_app()

def seed():
    with app.app_context():
        print("Resetting database...")
        db.drop_all()
        db.create_all()

        print("Creating demo users...")
        users_data = [
            {
                'username': 'alice',
                'email': 'alice@college.edu',
                'full_name': 'Alice Sharma',
                'phone': '+91 98765 11223',
                'location': 'Computer Science Dept, Block C',
                'password': 'password123'
            },
            {
                'username': 'bob',
                'email': 'bob@college.edu',
                'full_name': 'Bob Jenkins',
                'phone': '+91 98765 22334',
                'location': 'Hostel 4, Room 302',
                'password': 'password123'
            },
            {
                'username': 'charlie',
                'email': 'charlie@college.edu',
                'full_name': 'Charlie Davis',
                'phone': '+91 98765 33445',
                'location': 'Electrical Engineering, Lab 2',
                'password': 'password123'
            },
            {
                'username': 'diana',
                'email': 'diana@college.edu',
                'full_name': 'Diana Prince',
                'phone': '+91 98765 44556',
                'location': 'Hostel 2, Room 108',
                'password': 'password123'
            }
        ]

        users = {}
        for u in users_data:
            user = User(
                username=u['username'],
                email=u['email'],
                full_name=u['full_name'],
                phone=u['phone'],
                location=u['location']
            )
            user.set_password(u['password'])
            db.session.add(user)
            users[u['username']] = user

        db.session.commit()
        print("Users created.")

        print("Adding sample books...")
        books_data = [
            {
                'title': 'Clean Code: A Handbook of Agile Software Craftsmanship',
                'author': 'Robert C. Martin',
                'genre': 'Computer Science & Tech',
                'isbn': '978-0132350884',
                'condition': 'Like New',
                'description': 'Even bad code can function. But if code isn\'t clean, it can bring a development organization to its knees. Essential reading for every software engineer.',
                'cover_url': 'https://images.unsplash.com/photo-1532012164546-f432f2e3dd44?auto=format&fit=crop&w=600&q=80',
                'owner': users['alice'],
                'is_available': True
            },
            {
                'title': 'Introduction to Algorithms (CLRS)',
                'author': 'Thomas H. Cormen, Charles E. Leiserson',
                'genre': 'Computer Science & Tech',
                'isbn': '978-0262033848',
                'condition': 'Good',
                'description': 'The bible of algorithmic design and analysis. Covers sorting, dynamic programming, graph algorithms, and NP-completeness.',
                'cover_url': 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=600&q=80',
                'owner': users['alice'],
                'is_available': True
            },
            {
                'title': 'Atomic Habits',
                'author': 'James Clear',
                'genre': 'Self-Help & Productivity',
                'isbn': '978-0735211292',
                'condition': 'Like New',
                'description': 'An easy & proven way to build good habits and break bad ones. Extremely practical framework for college students aiming for consistent study routines.',
                'cover_url': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80',
                'owner': users['bob'],
                'is_available': True
            },
            {
                'title': 'The Pragmatic Programmer: Your Journey to Mastery',
                'author': 'David Thomas, Andrew Hunt',
                'genre': 'Computer Science & Tech',
                'isbn': '978-0135957059',
                'condition': 'Good',
                'description': 'Filled with practical advice on career, software architecture, DRY principles, and debugging techniques.',
                'cover_url': 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=600&q=80',
                'owner': users['bob'],
                'is_available': False  # Currently borrowed
            },
            {
                'title': 'Sapiens: A Brief History of Humankind',
                'author': 'Yuval Noah Harari',
                'genre': 'History & Politics',
                'isbn': '978-0062316097',
                'condition': 'Fair',
                'description': '100,000 years ago, at least six human species inhabited the earth. Today there is just one. Us. How did our species succeed in the battle for dominance?',
                'cover_url': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=600&q=80',
                'owner': users['charlie'],
                'is_available': True
            },
            {
                'title': 'Dune',
                'author': 'Frank Herbert',
                'genre': 'Science Fiction & Fantasy',
                'isbn': '978-0441172719',
                'condition': 'Good',
                'description': 'Set on the desert planet Arrakis, Dune is the story of the boy Paul Atreides, heir to a noble family tasked with ruling an inhospitable world.',
                'cover_url': 'https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=600&q=80',
                'owner': users['diana'],
                'is_available': True
            },
            {
                'title': 'Deep Work: Rules for Focused Success in a Distracted World',
                'author': 'Cal Newport',
                'genre': 'Self-Help & Productivity',
                'isbn': '978-1455586691',
                'condition': 'Like New',
                'description': 'Deep work is the ability to focus without distraction on a cognitively demanding task. A must-read before semester exams.',
                'cover_url': 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=600&q=80',
                'owner': users['diana'],
                'is_available': True
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'genre': 'Literature & Classics',
                'isbn': '978-0060935467',
                'condition': 'Good',
                'description': 'A masterpiece of American literature exploring moral courage, justice, and childhood in the deep South.',
                'cover_url': 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80',
                'owner': users['charlie'],
                'is_available': True
            }
        ]

        books = []
        for b in books_data:
            book = Book(
                title=b['title'],
                author=b['author'],
                genre=b['genre'],
                isbn=b['isbn'],
                condition=b['condition'],
                description=b['description'],
                cover_url=b['cover_url'],
                owner=b['owner'],
                is_available=b['is_available']
            )
            db.session.add(book)
            books.append(book)

        db.session.commit()
        print(f"Added {len(books)} sample books.")

        print("Adding sample reviews...")
        reviews_data = [
            {
                'book': books[0],  # Clean Code
                'user': users['bob'],
                'rating': 5,
                'comment': 'Transformed how I write functions and names! Every 3rd year student must read this before campus placements.'
            },
            {
                'book': books[0],  # Clean Code
                'user': users['charlie'],
                'rating': 4,
                'comment': 'Great principles, especially the chapters on meaningful names and error handling.'
            },
            {
                'book': books[2],  # Atomic Habits
                'user': users['alice'],
                'rating': 5,
                'comment': 'The 2-minute rule helped me study consistently every evening. Book in great physical condition too!'
            },
            {
                'book': books[3],  # Pragmatic Programmer
                'user': users['alice'],
                'rating': 5,
                'comment': 'Currently reading this. Incredible insights on orthogonality and refactoring.'
            },
            {
                'book': books[5],  # Dune
                'user': users['bob'],
                'rating': 4,
                'comment': 'Fascinating world-building. Took me about 2 weeks to finish.'
            }
        ]

        for r in reviews_data:
            rev = Review(
                book=r['book'],
                user=r['user'],
                rating=r['rating'],
                comment=r['comment']
            )
            db.session.add(rev)

        db.session.commit()
        print("Reviews added.")

        print("Creating sample borrow requests...")
        # 1. Approved request (Alice borrowed Pragmatic Programmer from Bob)
        req1 = BorrowRequest(
            book=books[3],
            borrower=users['alice'],
            owner=users['bob'],
            duration_days=14,
            message="Hey Bob, need this for my software engineering assignment. Can collect at cafeteria.",
            status='Approved',
            request_date=datetime.utcnow() - timedelta(days=5),
            action_date=datetime.utcnow() - timedelta(days=4)
        )
        db.session.add(req1)

        # 2. Pending request (Charlie requested Introduction to Algorithms from Alice)
        req2 = BorrowRequest(
            book=books[1],
            borrower=users['charlie'],
            owner=users['alice'],
            duration_days=21,
            message="Hi Alice, preparing for upcoming DSA lab exam. Would love to borrow your CLRS copy!",
            status='Pending',
            request_date=datetime.utcnow() - timedelta(hours=3)
        )
        db.session.add(req2)

        # 3. Returned request (Diana borrowed Atomic Habits from Bob and returned it)
        req3 = BorrowRequest(
            book=books[2],
            borrower=users['diana'],
            owner=users['bob'],
            duration_days=7,
            message="Hi Bob, would love to read this over the weekend.",
            status='Returned',
            request_date=datetime.utcnow() - timedelta(days=20),
            action_date=datetime.utcnow() - timedelta(days=19),
            return_date=datetime.utcnow() - timedelta(days=12)
        )
        db.session.add(req3)

        db.session.commit()
        print("Sample borrow requests seeded.")

        print("\n" + "=" * 60)
        print("[OK] DATABASE SEEDED SUCCESSFULLY!")
        print("Sample login credentials:")
        print("  - Username: alice    | Password: password123")
        print("  - Username: bob      | Password: password123")
        print("  - Username: charlie  | Password: password123")
        print("  - Username: diana    | Password: password123")
        print("=" * 60)

if __name__ == '__main__':
    seed()
