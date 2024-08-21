import os
from dotenv import load_dotenv
from flask import Flask
from store_data import DatabaseManager
from integrate_square import SquareIntegration

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
square_access_token = os.getenv("SQUARE_ACCESS_TOKEN")

if square_access_token is None:
    raise ValueError("No SQUARE_ACCESS_TOKEN found in environment variables.")

# Initialize database and Square integration
db_manager = DatabaseManager('sqlite:///payments.db')  # Change to your database URL
integration = SquareIntegration(square_access_token, db_manager)

# Webhook route
@app.route('/square/webhook', methods=['POST'])
def square_webhook():
    return integration.handle_webhook()

# Testing route to manually trigger a payment process
@app.route('/test_payment', methods=['POST'])
def test_payment():
    # Example transaction details for testing
    source_id = "cnon:card-nonce-ok"  # Replace with actual source ID from Square
    amount_money = {"amount": 1000, "currency": "USD"}
    idempotency_key = "UNIQUE_KEY_123"  # Ensure this key is unique for each transaction
    location_id = "LOCATION_ID"  # Replace with your Square location ID

    integration.process_transaction(source_id, amount_money, idempotency_key, location_id)
    return "Test payment processed.", 200

# Main execution
if __name__ == "__main__":
    app.run(port=5000)