from database import engine, Base

# Import all models so Base knows about them
from auth.models import User
from documents.models import Document
from chat.models import Conversation, Message

def create_tables():
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

if __name__ == "__main__":
    create_tables()