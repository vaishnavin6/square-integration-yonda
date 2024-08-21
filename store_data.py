from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, inspect
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
        self.check_table_creation()

    def check_table_creation(self):
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        if 'payments' in tables:
            logging.info("Table 'payments' exists and was created successfully.")
        else:
            logging.error("Table 'payments' does not exist. There was an issue creating the table.")

    def store_payment_data(self, payment_data):
        session = None
        try:
            payment_object = payment_data['data']['object'].get('payment')
            if not payment_object:
                raise ValueError("Payment data is missing 'payment' object.")

            payment_id = payment_object['id']
            logging.info(f"Processing payment ID {payment_id} with status {payment_object.get('status', 'UNKNOWN')}")

            session = self.Session()
            existing_payment = session.query(Payment).filter_by(payment_id=payment_id).first()

            if existing_payment:
                logging.info(f"Payment with ID {payment_id} exists. Updating record.")
                existing_payment.amount = payment_object['amount_money']['amount'] / 100.0
                existing_payment.currency = payment_object['amount_money']['currency']
                existing_payment.status = payment_object.get('status', 'UNKNOWN')
                existing_payment.timestamp = datetime.utcnow()
            else:
                logging.info(f"Inserting new payment record for ID {payment_id}")
                payment = Payment(
                    payment_id=payment_id,
                    amount=payment_object['amount_money']['amount'] / 100.0,
                    currency=payment_object['amount_money']['currency'],
                    status=payment_object.get('status', 'UNKNOWN')
                )
                session.add(payment)

            session.commit()
            logging.info(f"Payment with ID {payment_id} stored successfully.")
        except Exception as e:
            logging.error(f"Failed to store payment data: {e}")
        finally:
            if session:
                session.close()

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db_manager = DatabaseManager('sqlite:///payments.db')