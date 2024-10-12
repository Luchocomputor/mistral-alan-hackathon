import json
import requests
import streamlit as st

from mistralai import Mistral

# Set your API key and agent ID for the Mistral API
api_key = "9xI84xYuI7PIabGQ3KvtxYhhXz9P5SYP"
# model = "mistral-large-latest"
agent_id = "ag:68998b79:20241012:untitled-agent:5aec32b4"

# Initialize Mistral client
client = Mistral(api_key=api_key)

# Load storage file (assuming JSON format)
def load_data():
    try:
        with open('data/food_stock.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save to storage file
def save_data(data):
    with open('data/food_stock.json', 'w') as f:
        json.dump(data, f, indent=4)


# Function to call the language model (Mistral API)
def call_language_model(text_input=None, image=None):
    if not text_input:
        return {"error": "No text provided."}

    try:
        # Call the Mistral API
        chat_response = client.agents.complete(
            agent_id=agent_id,
            messages=[
                {
                    "role": "user",
                    "content": text_input,
                }
            ]
        )
        # Extract the response content
        response_content = chat_response.choices[0].message.content
        print(response_content)

        return {"response": response_content}

    except Exception as e:
        return {"error": str(e)}


# Function to render chat messages as bubbles
def render_message_bubbles(chat_log):
    for log in chat_log:
        if log['user'] == 'User':
            # User message bubble (align left)
            st.markdown(f"""
            <div style='text-align: left; background-color: #D4E6F1; 
                        border-radius: 10px; padding: 10px; margin: 10px 0;'>
                <strong>User:</strong><br>{log['message']}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Bot message bubble (align right)
            st.markdown(f"""
            <div style='text-align: right; background-color: #FAD7A0; 
                        border-radius: 10px; padding: 10px; margin: 10px 0;'>
                <strong>Bot:</strong><br>{log['message']}
            </div>
            """, unsafe_allow_html=True)



# Streamlit interface for chatbot interaction
def chatbot_interaction():
    st.title("Chatbot Discussion with LLM")

    # Conversation log
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []

    # Chat history display at the top
    st.subheader("Chat History")
    render_message_bubbles(st.session_state.chat_log)

    # Text input at the bottom
    st.markdown("<hr>", unsafe_allow_html=True)
    user_input = st.text_input("Type your message...", key="input_field")

    # Image upload at the bottom (optional for now)
    image_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

    # Send message button
    if st.button("Send", key="send_button"):
        if user_input or image_file:
            # Call language model API
            response = call_language_model(user_input, image_file)

            if "error" in response:
                st.error(f"Error: {response['error']}")
            else:
                bot_response = response.get("response", "No response from the model")

                # Update chat log
                st.session_state.chat_log.append({"user": "User", "message": user_input or "Image sent"})
                st.session_state.chat_log.append({"user": "Bot", "message": bot_response})

                # Clear input field and rerun
                st.rerun()

# Streamlit interface for managing food stocks
def manage_food_stocks():
    stock = load_data()

    # Display current stock and allow updates
    st.subheader("Current Stock")
    for item, info in stock.items():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text(item.capitalize())  # Item name
        with col2:
            new_quantity = st.number_input(f"Quantity ({info['unit']})", value=float(info['quantity']), key=item)
        with col3:
            if st.button(f"Update", key=f"update_{item}"):
                stock[item]['quantity'] = new_quantity
                save_data(stock)
                st.success(f"Updated {item} to {new_quantity} {info['unit']}")

    # Add new item to stock
    st.subheader("Add New Item")
    new_item_name = st.text_input("Item name", "")
    new_item_unit = st.selectbox("Unit", ["pieces", "grams", "kilograms", "liters"])
    new_item_quantity = st.number_input("Quantity", min_value=0.0, step=0.1, key="new_item")

    if st.button("Add Item"):
        if new_item_name and new_item_quantity > 0:
            if new_item_name not in stock:
                stock[new_item_name] = {"unit": new_item_unit, "quantity": new_item_quantity}
                save_data(stock)
                st.success(f"Added {new_item_name} with {new_item_quantity} {new_item_unit}")
            else:
                st.error(f"{new_item_name} already exists. Please update the quantity instead.")
        else:
            st.error("Please provide a valid item name and quantity.")


# Streamlit layout
def main():
    st.title("Food Stock Management")
    # Tabs for the app
    tab1, tab2, tab3 = st.tabs(["Chat with LLM", "Manage Food Stocks", "Tab 3"])

    with tab1:
        chatbot_interaction()
    
    with tab2:
        manage_food_stocks()
    

if __name__ == "__main__":
    main()

