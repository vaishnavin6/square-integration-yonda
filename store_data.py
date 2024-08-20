from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

Base = declarative_base()

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def store_payment_data(self, payment_data):
        session = self.Session()
        payment = Payment(
            payment_id=payment_data['id'],
            amount=payment_data['amount_money']['amount'] / 100.0,  # Convert cents to dollars
            currency=payment_data['amount_money']['currency'],
            status=payment_data['status']
        )
        session.add(payment)
        session.commit()
        logging.info("Payment data stored in the database.")
        session.close()