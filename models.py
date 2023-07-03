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


def run_analysis():
    ten_minutes_ago = datetime.now() - timedelta(minutes=10)
    messages = session.query(Message).filter(Message.time >= ten_minutes_ago).all()

    grouped_messages = {}
    for message in messages:
        if message.chat_id not in grouped_messages:
            grouped_messages[message.chat_id] = []

        grouped_messages[message.chat_id].append(message)

    # Process the grouped messages as needed
    chats_to_alert = []

    for chat_id, chat_messages in grouped_messages.items():
        print(f"Chat ID: {chat_id}")
        sentiment_score_sum = 0
        for message in chat_messages:
            sentiment_score_sum += message.sentiment_score
            print(f"Message ID: {message.id}, Text: {message.text}")
        sentiment_avg = sentiment_score_sum / len(chat_messages)

        if sentiment_avg > 0.4:
            chats_to_alert.append(chat_id)

    parents_to_alert = [session.query(Chat).get(chat_id).parent_id for chat_id in chats_to_alert]

    return parents_to_alert
