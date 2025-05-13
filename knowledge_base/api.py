from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Load data from JSON files
def load_data(filename):
    file_path = os.path.join(os.path.dirname(__file__), 'data', filename)
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}

# Calculate token count (rough estimate)
def estimate_tokens(text):
    # Simple estimation: ~4 chars per token on average
    return len(text) // 4

# Function to chunk responses to stay under token limit
def chunk_response(data, max_tokens=800):
    json_data = json.dumps(data)
    
    # If already under the limit, return as is
    if estimate_tokens(json_data) <= max_tokens:
        return [data]
    
    # Otherwise, need to chunk the data
    chunks = []
    
    # Handle different data structures appropriately
    if isinstance(data, dict) and "outlets" in data:
        # Split outlets into chunks
        outlets = data["outlets"]
        chunk_size = 2  # Adjust based on actual token size
        
        for i in range(0, len(outlets), chunk_size):
            chunk = {"outlets": outlets[i:i+chunk_size]}
            chunks.append(chunk)
    
    elif isinstance(data, dict) and "faqs" in data:
        # Split FAQs into chunks
        faqs = data["faqs"]
        chunk_size = 3  # Adjust based on actual token size
        
        for i in range(0, len(faqs), chunk_size):
            chunk = {"faqs": faqs[i:i+chunk_size]}
            chunks.append(chunk)
    
    elif isinstance(data, dict) and "categories" in data:
        # Split menu categories into chunks
        for category in data["categories"]:
            chunk = {"categories": [category]}
            chunks.append(chunk)
    
    else:
        # Generic chunking for other data types
        chunks.append({"message": "Data too large to display in full. Please narrow your query."})
    
    return chunks

@app.route('/api/outlets', methods=['GET'])
def get_outlets():
    location = request.args.get('location', '').lower()
    
    if location == 'delhi':
        data = load_data('delhi_outlets.json')
    elif location == 'bangalore':
        data = load_data('bangalore_outlets.json')
    else:
        # Return both if no specific location
        delhi_data = load_data('delhi_outlets.json')
        bangalore_data = load_data('bangalore_outlets.json')
        
        all_outlets = []
        if "outlets" in delhi_data:
            all_outlets.extend(delhi_data["outlets"])
        if "outlets" in bangalore_data:
            all_outlets.extend(bangalore_data["outlets"])
            
        data = {"outlets": all_outlets}
    
    # Get chunk index (for pagination)
    chunk_index = int(request.args.get('chunk', 0))
    chunks = chunk_response(data)
    
    if chunk_index < 0 or chunk_index >= len(chunks):
        return jsonify({"error": "Invalid chunk index"})
    
    response = chunks[chunk_index]
    response["total_chunks"] = len(chunks)
    response["current_chunk"] = chunk_index
    
    return jsonify(response)

@app.route('/api/menu', methods=['GET'])
def get_menu():
    category = request.args.get('category', '').lower()
    data = load_data('menu.json')
    
    if category and "categories" in data:
        filtered_categories = [c for c in data["categories"] if c["name"].lower() == category]
        if filtered_categories:
            data = {"categories": filtered_categories}
    
    chunk_index = int(request.args.get('chunk', 0))
    chunks = chunk_response(data)
    
    if chunk_index < 0 or chunk_index >= len(chunks):
        return jsonify({"error": "Invalid chunk index"})
    
    response = chunks[chunk_index]
    response["total_chunks"] = len(chunks)
    response["current_chunk"] = chunk_index
    
    return jsonify(response)

@app.route('/api/faq', methods=['GET'])
def get_faq():
    keyword = request.args.get('keyword', '').lower()
    data = load_data('faq.json')
    
    if keyword and "faqs" in data:
        filtered_faqs = [faq for faq in data["faqs"] 
                         if keyword in faq["question"].lower() or keyword in faq["answer"].lower()]
        if filtered_faqs:
            data = {"faqs": filtered_faqs}
    
    chunk_index = int(request.args.get('chunk', 0))
    chunks = chunk_response(data)
    
    if chunk_index < 0 or chunk_index >= len(chunks):
        return jsonify({"error": "Invalid chunk index"})
    
    response = chunks[chunk_index]
    response["total_chunks"] = len(chunks)
    response["current_chunk"] = chunk_index
    
    return jsonify(response)

@app.route('/api/query', methods=['GET'])
def unified_query():
    query = request.args.get('q', '').lower()
    
    # Simple intent detection based on keywords
    if any(word in query for word in ['location', 'outlet', 'branch', 'restaurant']):
        if 'delhi' in query:
            return get_outlets_by_location('delhi')
        elif 'bangalore' in query or 'bengaluru' in query:
            return get_outlets_by_location('bangalore')
        else:
            return get_outlets()
    
    elif any(word in query for word in ['menu', 'food', 'dish', 'meal']):
        if 'starter' in query:
            return get_menu_by_category('starters')
        elif 'main' in query:
            return get_menu_by_category('main course')
        else:
            return get_menu()
    
    elif any(word in query for word in ['faq', 'question', 'how', 'what', 'why']):
        for keyword in ['reservation', 'booking', 'vegan', 'buffet', 'grill']:
            if keyword in query:
                return get_faq_by_keyword(keyword)
        return get_faq()
    
    # Default response if no intent is matched
    return jsonify({
        "message": "I can help you with information about our outlets, menu, or answer frequently asked questions. Please specify what you're looking for."
    })

def get_outlets_by_location(location):
    return get_outlets.__wrapped__(location=location)

def get_menu_by_category(category):
    return get_menu.__wrapped__(category=category)

def get_faq_by_keyword(keyword):
    return get_faq.__wrapped__(keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True, port=5000)