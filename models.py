from sqlalchemy import create_engine, Column, String, ForeignKey, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date, datetime, timedelta

# Create the engine and connect to the PostgreSQL database
engine = create_engine('postgresql://user:password@localhost:5432/ido')
Session = sessionmaker(bind=engine)
session = Session()

# Create a base class for declarative models
Base = declarative_base()


class Parent(Base):
    __tablename__ = 'parents'
    id = Column(String, primary_key=True)
    chats = relationship("Chat", backref="parent")


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(String, primary_key=True)
    parent_id = Column(String, ForeignKey('parents.id'))
    name = Column(String)
    messages = relationship("Message", backref="chat")


class Message(Base):
    __tablename__ = 'messages'
    id = Column(String, primary_key=True)
    chat_id = Column(String, ForeignKey('chats.id'))
    text = Column(String)
    sender = Column(String)
    sentiment_score = Column(Float)
    time = Column(Date)


# Create the tables in the database if they don't exist
Base.metadata.create_all(engine)


def save_parent(parent_id):
    parent = Parent(id=parent_id)
    session.add(parent)
    session.commit()
    print(f"Parent with ID '{parent_id}' saved successfully!")


def save_chat(parent_id, chat_id, chat_name):
    parent = session.query(Parent).get(parent_id)

    if parent is None:
        # Handle the case where the parent doesn't exist
        print(f"Parent with ID '{parent_id}' does not exist.")
        save_parent(parent_id)

    chat = Chat(id=chat_id, parent_id=parent_id, chat_name=chat_name)
    session.add(chat)
    session.commit()
    print(f"Chat with ID '{chat_id}' saved successfully!")


def save_message(chat_id, text, sender, sentiment_score):
    chat = session.query(Chat).get(chat_id)

    if chat is None:
        # Handle the case where the chat doesn't exist
        print(f"Chat with ID {chat_id} does not exist.")
        return

    new_message = Message(
        chat_id=chat_id,
        text=text,
        sender=sender,
        sentiment_score=sentiment_score,
        time=date.today()
    )

    session.add(new_message)
    session.commit()
    print("Message saved successfully!")


def get_parents_to_alert(minutes, sentiment_minimum):
    minutes_ago = datetime.now() - timedelta(minutes)

    # Query to fetch parent entities, their chats, and messages meeting the criteria
    results = session.query(Parent, Chat.name, Message) \
        .join(Chat, Parent.id == Chat.parent_id) \
        .join(Message, Chat.id == Message.chat_id) \
        .filter(Message.time >= minutes_ago) \
        .group_by(Parent, Chat.name) \
        .having(func.avg(Message.sentiment_score) >= sentiment_minimum) \
        .all()

    return results
