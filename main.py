from flask import Flask
from store_data import DatabaseManager
from integrate_square import SquareIntegration

# Initialize Flask app
app = Flask(__name__)

# Initialize database and Square integration
db_manager = DatabaseManager('sqlite:///payments.db')  # Change to your database URL
square_access_token = "YOUR_SQUARE_ACCESS_TOKEN"  # Replace with your Square Access Token
integration = SquareIntegration(square_access_token, db_manager)

# Webhook route
@app.route('/square/webhook', methods=['POST'])
def square_webhook():
    return integration.handle_webhook()

# Main execution
if __name__ == "__main__":
    app.run(port=5000)