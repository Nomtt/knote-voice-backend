import os
import uuid
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI

# 1. Initialize the App
app = Flask(__name__)
CORS(app)

# === IN-MEMORY DATABASE (Comprehensive Menu) ===
MENU_DB = [
    # === BURGERS & SANDWICHES ===
    {"id": "1", "name": "Beef Burger", "price": 6.5},
    {"id": "2", "name": "Sandwich", "price": 5.5},
    # === RICE & NOODLES ===
    {"id": "3", "name": "Hainanese Chicken Rice", "price": 5},
    # === SIDES ===
    {"id": "9", "name": "French Fries", "price": 2.5},
    # === DRINKS ===
    {"id": "14", "name": "Diet Coke", "price": 1.5},
]

# === ROUTE 1: THE HOMEPAGE ===
@app.route('/')
def index():
    return send_file('index.html')

# === ROUTE 2: MENU API (Frontend uses this) ===
@app.route('/menu', methods=['GET'])
def get_menu():
    """Returns the full list of menu items."""
    return jsonify({"items": MENU_DB})

@app.route('/menu', methods=['POST'])
def add_menu_item():
    """Adds a new item to the menu via HTTP."""
    data = request.json
    new_item = {
        "id": str(uuid.uuid4()),
        "name": data.get('name'),
        "price": int(data.get('price', 0))
    }
    MENU_DB.append(new_item)
    return jsonify(new_item)

@app.route('/menu/<item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    """Deletes an item from the menu."""
    global MENU_DB
    MENU_DB = [item for item in MENU_DB if item['id'] != item_id]
    return jsonify({"success": True})

# 2. Connect to OpenAI
# IMPORTANT: Make sure 'OPENAI_API_KEY' is in your Secrets (Environment Variables)
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# 3. The Logic (The "Brain")
@app.route('/process_audio', methods=['POST'])
def process_audio():
    # Validation
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files['file']
    unique_filename = f"temp_{uuid.uuid4()}.mp3"
    audio_file.save(unique_filename)

    try:
        audio_file_read = open(unique_filename, "rb")
        print("Calling Api1 (Whisper)...")

        # === DYNAMIC CONTEXT INJECTION ===
        menu_names = ", ".join([item['name'] for item in MENU_DB])

        # 1. Transcribe
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file_read,
            language="en",
            prompt=f"Menu: {menu_names}. Context: Food ordering. Keywords: Kosong, Siew Dai, Takeaway.",
            temperature=0.0
        )
        user_text = transcript.text
        print(f"User said: {user_text}")

        # === HYBRID SYSTEM PROMPT ===
        SYSTEM_PROMPT = f"""
        You are an AI Cashier. Extract data into strict JSON.

        ### CONTEXT - AVAILABLE MENU ITEMS:
        {menu_names}
        (INSTRUCTION: Priority is to match the names above.
         BUT, if the user orders a food item that is NOT listed, YOU MUST STILL EXTRACT IT. 
         Do not return an empty result. Create a new item name based on what you hear.)

        ### OUTPUT LANGUAGE POLICY (STRICT)
        - ALL output fields MUST be in ENGLISH ONLY.
        - Item names MUST be returned in CANONICAL ENGLISH (Title Case).
        - Modifiers MUST be returned in ENGLISH ONLY (Title Case).
        - Quantity MUST be numeric.

        ### JSON SCHEMA:
        {{
          "intent": "TRANSACTION" | "SYSTEM" | "ADD_TO_MENU" | null,
          "global_command": "CLEAR_CART" | "CHECKOUT" | "SHOW_CART" | null,
          "results": [
            {{
              "action": "add" | "remove",
              "item": "string (Title Case)",
              "quantity": integer,
              "price": number or null,
              "modifiers": ["string"]
            }}
          ]
        }}

        ### LOGIC PRIORITY & TRIGGERS:
        1. **SYSTEM COMMANDS**:
           - "Clear cart", "Cancel order" -> Set "global_command": "CLEAR_CART"
           - "Checkout", "Bill please" -> Set "global_command": "CHECKOUT"
           - "Show cart", "What did I order" -> Set "global_command": "SHOW_CART"

        2. **MENU UPDATES (Admin Mode)**:
           - Trigger: "Menu change add [Item] [Price]", "Add new item [Item]"
           - Action: Set "intent": "ADD_TO_MENU"

        3. **TRANSACTIONS (Ordering)**:
           - "Add [Item]", "I want [Item]" -> "action": "add"
           - "Remove [Item]", "Cancel [Item]" -> "action": "remove"
           - "Change [A] to [B]" -> Remove A, Add B.

        ### MODIFIER MAPPING (Strict Localized Rules):
        - kosong / no sugar / sugar free -> No Sugar
        - siew dai / less sugar -> Less Sugar
        - takeaway / dabao / to go -> Takeaway
        - no ice / warm -> No Ice
        - less ice -> Less Ice
        - not spicy / no chili -> No Chili

        ### BEHAVIORAL SAFETY RULES:
        - If input is irrelevant noise ("hello", "testing") -> Return "results": []
        - Do NOT guess item names if they are unclear.
        """

        # 2. Extract JSON
        print("Calling Api2 (GPT)...")
        completion = client.chat.completions.create(
            model="gpt-4o-2024-08-06", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            response_format={ "type": "json_object" },
            temperature=0
        )

        json_response_str = completion.choices[0].message.content
        print(f"AI Response: {json_response_str}") 

        data = json.loads(json_response_str)

        # === SERVER-SIDE LOGIC HANDLERS ===

        intent = data.get("intent")
        global_command = data.get("global_command")
        results = data.get("results", [])

        # A. Handle System Commands
        if global_command == "CLEAR_CART":
            print(">>> COMMAND: CLEAR CART")
        elif global_command == "CHECKOUT":
            print(">>> COMMAND: CHECKOUT")

        # B. Handle Menu Updates (Explicit Admin Mode)
        elif intent == "ADD_TO_MENU" and results:
            for entry in results:
                # 1. Create and Save to Database
                new_db_item = {
                    "id": str(uuid.uuid4()),
                    "name": item_name, 
                    "price": float(new_price) # <--- Changed to float
                }
                MENU_DB.append(new_db_item)

                # 2. Add to Cart
                order_item["price"] = float(new_price) # <--- Changed to floata
                
                print(f"Added to DB: {new_db_item}")

        # C. Combined Handler: Transactions + Auto-Add New Items
        # We accept "TRANSACTION" OR if intent is None/Null but we have results
        elif (intent == "TRANSACTION" or intent is None) and results:
            valid_results = [] 

            for order_item in results:
                item_name = order_item.get("item")

                # 1. Price Lookup
                found = next((m for m in MENU_DB if m["name"].lower() == item_name.lower()), None)

                if found:
                    # CASE A: Existing Item found in DB
                    order_item["price"] = found["price"]
                    # Normalize action
                    raw_action = order_item.get("action")
                    order_item["action"] = "add" if not raw_action else str(raw_action).lower().strip()

                    # Add to valid results (Success)
                    valid_results.append(order_item)
                    print(f"Matched: {item_name} @ {found['price']}")

                else:
                    # CASE B: NEW ITEM -> Check Price first!
                    new_price = order_item.get("price")

                    if new_price is None or new_price == 0:
                        # ERROR: User didn't say the price
                        print(f"Error: Price missing for new item '{item_name}'")

                        # We create a special "error object" to send back to frontend
                        # But we DO NOT add it to the DB or Cart logic
                        error_response = {
                            "item": item_name,
                            "error": f"Price missing for {item_name}", 
                            "action": "error" # Special action flag for frontend
                        }
                        valid_results.append(error_response)

                    else:
                        # SUCCESS: User said "Add Lobster for 50"
                        print(f"Auto-Learning: Creating '{item_name}' @ {new_price}")

                        # 1. Create and Save to Database
                        new_db_item = {
                            "id": str(uuid.uuid4()),
                            "name": item_name, 
                            "price": int(new_price)
                        }
                        MENU_DB.append(new_db_item)

                        # 2. Add to Cart
                        order_item["price"] = int(new_price)
                        order_item["is_new"] = True 

                        # Normalize action
                        raw_action = order_item.get("action")
                        order_item["action"] = "add" if not raw_action else str(raw_action).lower().strip()

                        valid_results.append(order_item)

            # Update the response 
            data["results"] = valid_results
            # Force intent to TRANSACTION so frontend processes it
            data["intent"] = "TRANSACTION"

        # Cleanup
        audio_file_read.close()
        if os.path.exists(unique_filename):
            os.remove(unique_filename)

        return jsonify(data)

    except Exception as e:
        print(f"Error: {e}")
        if os.path.exists(unique_filename):
            os.remove(unique_filename)
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    # Host 0.0.0.0 is required for Replit to be accessible
    app.run(host='0.0.0.0', port=8080)
