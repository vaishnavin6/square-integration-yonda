import os
import logging
from dotenv import load_dotenv
from square.client import Client
from store_data import DatabaseManager

load_dotenv()

class SquareIntegration:
    def __init__(self):
        logging.info("Initializing Square Integration")
        self.client = Client(access_token=os.getenv("SQUARE_ACCESS_TOKEN"))
        self.location_id = os.getenv("SQUARE_LOCATION_ID")
        self.db_manager = DatabaseManager('sqlite:///payments.db')
        logging.info("Square Integration initialized successfully")

    def handle_webhook(self, payment_data):
        try:
            payment_object = payment_data.get('data', {}).get('object', {}).get('payment', {})
            payment_id = payment_object.get('id', 'Unknown ID')
            logging.info(f"Webhook received for payment ID: {payment_id}")
            logging.debug(f"Full webhook data: {payment_data}")

            if not payment_object:
                raise ValueError("Missing payment object in webhook data.")

            # Store payment data
            self.db_manager.store_payment_data(payment_data)
            logging.info(f"Payment data processed successfully for ID: {payment_id}")
        except Exception as e:
            logging.error(f"Error handling webhook for payment ID {payment_data.get('id', 'Unknown ID')}: {e}")

    def capture_payment(self, source_id, amount_money, idempotency_key):
        try:
            logging.info(f"Initiating payment capture with idempotency key: {idempotency_key}")
            body = {
                "idempotency_key": idempotency_key,
                "amount_money": amount_money,
                "source_id": source_id
            }
            logging.debug(f"Payment capture request body: {body}")
            result = self.client.payments.create_payment(body)
            if result.is_success():
                payment_id = result.body['payment']['id']
                logging.info(f"Payment captured successfully. Payment ID: {payment_id}")
                logging.debug(f"Payment capture response: {result.body}")
                return result.body
            elif result.is_error():
                logging.error(f"Payment capture failed: {result.errors}")
                logging.debug(f"Failed payment capture response: {result.errors}")
                return None
        except Exception as e:
            logging.error(f"Error capturing payment: {e}")
            return None

    def process_transaction(self, source_id, amount_money, idempotency_key):
        logging.info(f"Processing transaction with idempotency key: {idempotency_key}")
        payment_result = self.capture_payment(source_id, amount_money, idempotency_key)
        if payment_result:
            logging.info(f"Storing transaction data for payment ID: {payment_result['payment']['id']}")
            self.db_manager.store_payment_data(payment_result)
        else:
            logging.warning(f"Transaction processing failed for idempotency key: {idempotency_key}")