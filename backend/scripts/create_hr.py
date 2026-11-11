from getpass import getpass

from sqlalchemy.exc import IntegrityError

from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def create_hr_account():

    db = SessionLocal()

    try:
        # Get HR account details
        full_name = input("Enter HR Name: ")
        email = input("Enter HR Email: ")
        password = getpass("Enter HR Password: ")

        # Check whether email already exists
        existing_user = db.query(User).filter(
            User.email == email
        ).first()

        if existing_user:
            print("This email is already registered.")
            return

        # Hash password
        hashed_password = hash_password(password)

        # Create HR user
        new_hr = User(
            full_name=full_name,
            email=email,
            password_hash=hashed_password,
            role="hr",
            is_active=True
        )

        # Save HR account
        db.add(new_hr)
        db.commit()
        db.refresh(new_hr)

        print("\nHR Account Created Successfully!")
        print("User ID:", new_hr.user_id)
        print("Name:", new_hr.full_name)
        print("Email:", new_hr.email)
        print("Role:", new_hr.role)

    except IntegrityError:
        db.rollback()
        print("Database error: Email may already exist.")

    except Exception as e:
        db.rollback()
        print("Error:", str(e))

    finally:
        db.close()


if __name__ == "__main__":
    create_hr_account()