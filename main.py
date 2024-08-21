import logging
from dotenv import load_dotenv
from integrate_square import SquareIntegration
from flask import Flask, request, jsonify

# Load environment variables
load_dotenv()

# Initialize Flask app and logging
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Square integration
square_integration = SquareIntegration()

@app.route("/webhook", methods=["POST"])
def square_webhook():
    payment_data = request.json
    if not payment_data:
        logging.error("No data received in webhook.")
        return jsonify({"status": "error", "message": "No data received"}), 400
    
    payment_object = payment_data.get('data', {}).get('object', {}).get('payment', {})
    payment_id = payment_object.get('id', 'Unknown ID')
    
    logging.info(f"Received webhook for payment ID: {payment_id}")
    logging.debug(f"Webhook full data: {payment_data}")

    try:
        square_integration.handle_webhook(payment_data)
        logging.info(f"Successfully processed webhook for payment ID: {payment_id}")
        response = {"status": "success"}
        status_code = 200
    except Exception as e:
        logging.error(f"Error processing webhook for payment ID: {payment_id}: {e}")
        response = {"status": "error", "message": str(e)}
        status_code = 500
    
    return jsonify(response), status_code

if __name__ == "__main__":
    logging.info("Starting Flask app for Square Integration")
    app.run(debug=True, port=5000)