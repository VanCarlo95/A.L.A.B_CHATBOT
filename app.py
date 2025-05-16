
# app.py

from flask import Flask, request, jsonify
# from flask_cors import CORS
from rasa.core.agent import Agent
import asyncio
import os
import sys
import glob
import logging
import tensorflow as tf
import time
import re

# Suppress tensorflow logging
tf.get_logger().setLevel('ERROR')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# In-memory message counters and histories
message_counts = {}
chat_histories = {}
# Store the mapping of sender_id to filename to ensure consistency
chat_file_mappings = {}

# Feedback message template
FEEDBACK_MESSAGE = "❌ You've reached the message limit. Thank you for testing our chatbot. Your participation in our study is crucial and would be greatly appreciated. <a href='https://2ly.link/26ajD'>Please continue here to provide your feedback</a>"

# Message limit
MESSAGE_LIMIT = 10

# Directory for chat histories
CHAT_HISTORY_DIR = "chat_histories"

def get_latest_model():
    models_dir = 'models'
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        raise FileNotFoundError(f"Created new models directory at {models_dir}")
    
    model_files = glob.glob(os.path.join(models_dir, '*.tar.gz'))
    if not model_files:
        raise FileNotFoundError(f"No model files found in {models_dir}")
    
    latest_model = max(model_files, key=os.path.getmtime)
    print(f"Loading model: {latest_model}")
    return latest_model

# Create chat history directory if it doesn't exist
if not os.path.exists(CHAT_HISTORY_DIR):
    os.makedirs(CHAT_HISTORY_DIR)
    print(f"Created chat history directory at {CHAT_HISTORY_DIR}")

def get_next_chat_filename(sender_id):
    """Generate an incremental filename for chat history"""
    # If this sender already has a filename, use it
    if sender_id in chat_file_mappings:
        return chat_file_mappings[sender_id]
    
    # Get all existing chat files
    existing_files = glob.glob(os.path.join(CHAT_HISTORY_DIR, "chat_history_*.txt"))
    
    # Extract the numeric parts from filenames
    numbers = []
    for filename in existing_files:
        basename = os.path.basename(filename)
        match = re.search(r'chat_history_(\d+)\.txt', basename)
        if match:
            numbers.append(int(match.group(1)))
    
    # Get the next number
    next_number = 1
    if numbers:
        next_number = max(numbers) + 1
    
    # Create new filename
    new_filename = os.path.join(CHAT_HISTORY_DIR, f"chat_history_{next_number:03d}.txt")
    
    # Store mapping for future use
    chat_file_mappings[sender_id] = new_filename
    
    return new_filename

try:
    model_path = get_latest_model()
    agent = Agent.load(model_path)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    raise

# With Chat Limit
@app.route('/webhooks/rest/webhook', methods=['POST', 'OPTIONS'])
async def webhook():
    if request.method == 'OPTIONS':
        # Comment out if for production
        response = jsonify({'status': 'OK'})
        # response.headers.add('Access-Control-Allow-Origin', '*')
        # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        # response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200
        
    try:
        data = request.json
        message = data.get('message')
        sender_id = data.get('sender', 'default')
        
        print(f"Received message: {message} from sender: {sender_id}")
        
        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Get chat history filename for this sender
        chat_filename = get_next_chat_filename(sender_id)

        # Track message count
        count = message_counts.get(sender_id, 0) + 1
        message_counts[sender_id] = count

        # Get timestamp for the message
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Append to chat history
        if sender_id not in chat_histories:
            chat_histories[sender_id] = []
            # Add header information to new chat histories
            chat_histories[sender_id].append(f"Chat History for User ID: {sender_id}")
            chat_histories[sender_id].append(f"Started: {timestamp}")
            chat_histories[sender_id].append("=" * 50)
        
        chat_histories[sender_id].append(f"[{timestamp}] User: {message}")

        # Limit logic - if already over limit, only return feedback message
        if count > MESSAGE_LIMIT:
            # Add a note that the limit was reached
            chat_histories[sender_id].append(f"[{timestamp}] SYSTEM: Message limit reached")
            
            # Save chat history to file
            with open(chat_filename, "w", encoding="utf-8") as f:
                for line in chat_histories[sender_id]:
                    f.write(line + "\n")
            
            return jsonify([{
                "recipient_id": sender_id,
                "text": FEEDBACK_MESSAGE
            }])

        # Get response from Rasa agent for normal messages
        responses = await agent.handle_text(message, sender_id=sender_id)
        formatted_responses = []

        # Track predicted action and confidence
        if responses:
            # Extract metadata if available
            metadata = {}
            for resp in responses:
                if isinstance(resp, dict) and 'metadata' in resp:
                    metadata = resp.get('metadata', {})
                    break
            
            predicted_action = metadata.get('action_name', 'unknown')
            predicted_action_conf = metadata.get('action_confidence', 'N/A')
        else:
            predicted_action = 'none'
            predicted_action_conf = '0'

        # Append action to chat history
        chat_histories[sender_id].append(f"[{timestamp}] System: Predicted Action: {predicted_action} with confidence {predicted_action_conf}")

        # Format responses and store them
        for response in responses:
            if isinstance(response, dict) and 'text' in response:
                formatted_responses.append({
                    'recipient_id': sender_id,
                    'text': response['text']
                })
                chat_histories[sender_id].append(f"[{timestamp}] Bot: {response['text']}")
            elif isinstance(response, str):
                formatted_responses.append({
                    'recipient_id': sender_id,
                    'text': response
                })
                chat_histories[sender_id].append(f"[{timestamp}] Bot: {response}")

        # If this is exactly the 10th message, add feedback message as separate response
        if count == MESSAGE_LIMIT:
            # Add feedback message to the list of responses (as a separate bubble)
            formatted_responses.append({
                'recipient_id': sender_id,
                'text': FEEDBACK_MESSAGE
            })
            chat_histories[sender_id].append(f"[{timestamp}] Bot: {FEEDBACK_MESSAGE}")
            chat_histories[sender_id].append(f"[{timestamp}] SYSTEM: Message limit reached")

        # Save chat history to file
        with open(chat_filename, "w", encoding="utf-8") as f:
            for line in chat_histories[sender_id]:
                f.write(line + "\n")

        return jsonify(formatted_responses)

    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    print("\nRasa webhook server is running on http://localhost:5005")
    app.run(host='0.0.0.0', port=5005, debug=False)
