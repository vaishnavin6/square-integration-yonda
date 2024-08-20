import squareup
import logging
from flask import request, jsonify
from squareup.client import Client

class SquareIntegration:
    def __init__(self, square_access_token, db_manager):
        self.client = Client(access_token=square_access_token, environment="sandbox")  # Use "production" for live
        self.db_manager = db_manager
    
    def handle_webhook(self):
        try:
            webhook_data = request.json
            logging.info(f"Received webhook: {webhook_data}")
            
            if 'type' in webhook_data and webhook_data['type'] == 'payment.created':
                payment_data = webhook_data['data']['object']
                logging.info(f"Payment Data: ID: {payment_data['id']}, Amount: {payment_data['amount_money']['amount']}, Currency: {payment_data['amount_money']['currency']}, Status: {payment_data['status']}")
                self.db_manager.store_payment_data(payment_data)
                
            return jsonify({'status': 'success'}), 200
        
        except Exception as e:
            logging.error(f"Error handling webhook: {e}")
            return jsonify({'status': 'error'}), 500

    #For testing
    def capture_payment(self, source_id, amount_money, idempotency_key, location_id):
        try:
            body = {
                "idempotency_key": idempotency_key,
                "amount_money": amount_money,
                "source_id": source_id
            }
            result = self.client.payments.create_payment(body)
            if result.is_success():
                payment_id = result.body['payment']['id']
                payment_status = result.body['payment']['status']
                payment_amount = result.body['payment']['amount_money']['amount']
                currency = result.body['payment']['amount_money']['currency']
                logging.info(f"Payment captured successfully. ID: {payment_id}, Status: {payment_status}, Amount: {payment_amount} {currency}")
                return result.body
            elif result.is_error():
                logging.error(f"Payment capture failed: {result.errors}")
                return None
        except Exception as e:
            logging.error(f"Error capturing payment: {e}")
            return None

    #For testing
    def process_transaction(self, source_id, amount_money, idempotency_key, location_id):
        payment_data = self.capture_payment(source_id, amount_money, idempotency_key, location_id)
        if payment_data:
            self.db_manager.store_payment_data(payment_data['payment'])  # Store in DB