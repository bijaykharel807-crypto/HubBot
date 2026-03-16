import streamlit as st
import os
import requests
from datetime import datetime

# Load OpenRouter API key from Streamlit secrets or environment variable
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("OpenRouter API key not found. Please set it as an environment variable or add it to `.streamlit/secrets.toml`.")
    st.stop()

# Define constants
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
# You can change this to any model from https://openrouter.ai/models
MODEL_NAME = "meta-llama/llama-3.3-70b-instruct:free"   # Free model

# Optional: Identify your app to OpenRouter (helps with support)
SITE_URL = "https://yourapp.com"   # Replace with your actual URL if deployed
APP_NAME = "HubBot"

# Set page configuration
st.set_page_config(page_title="HubBot", page_icon="🤖", layout="centered")

# Define custom CSS (unchanged)
st.markdown("""
<style>
    /* Overall background */
    .stApp {
        background-color: #f5f8fa;
    }
    /* Chat message container */
    .stChatMessage {
        padding: 0 !important;
    }
    /* User message bubble */
    .stChatMessage[data-testid="chat-message-user"] div[data-testid="chat-message-content"] {
        background-color: #0b2b4a !important;
        color: white !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 12px 16px !important;
        max-width: 80%;
        margin-left: auto;
    }
    /* Assistant message bubble */
    .stChatMessage[data-testid="chat-message-assistant"] div[data-testid="chat-message-content"] {
        background-color: #f1f3f5 !important;
        color: #1e2a3a !important;
        border-radius: 18px 18px 18px 4px !important;
        padding: 12px 16px !important;
        max-width: 80%;
    }
    /* Timestamp style */
    .timestamp {
        font-size: 11px;
        color: #8a9aa8;
        text-align: right;
        margin-top: 6px;
    }
    .user-timestamp {
        color: #b0c4de;
    }
    /* Options container – 4 buttons in a row */
    .option-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 16px 0;
        justify-content: center;
    }
    /* Individual option button (Streamlit button override) */
    div.stButton > button {
        background: white !important;
        border: 1px solid #ccd7e4 !important;
        border-radius: 30px !important;
        padding: 8px 16px !important;
        font-size: 14px !important;
        color: #1e2a3a !important;
        font-weight: normal !important;
        transition: all 0.2s !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        width: 100% !important;
        justify-content: center !important;
    }
    div.stButton > button:hover {
        background: #e9ecf0 !important;
        border-color: #0b2b4a !important;
    }
    /* Disclaimer and AI warning */
    .disclaimer {
        font-size: 12px;
        color: #5a6b7c;
        margin: 16px 0 8px;
        line-height: 1.4;
        text-align: center;
    }
    .disclaimer a {
        color: #0b2b4a;
        text-decoration: none;
    }
    .ai-warning {
        font-size: 12px;
        color: #8a9aa8;
        font-style: italic;
        margin-bottom: 6px;
        text-align: center;
    }
    /* Hide Streamlit footer */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "first_message_sent" not in st.session_state:
    st.session_state.first_message_sent = False

# Define function to call OpenRouter API
def call_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": SITE_URL,          # Optional, for rankings on openrouter.ai
        "X-Title": APP_NAME                 # Optional, shows in logs
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# Display header with logo (optional)
logo_path = "hubspot_logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=150)
else:
    st.markdown("<h2 style='text-align: center; color:#0b2b4a;'>HubBot</h2>", unsafe_allow_html=True)

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])
        if "timestamp" in msg:
            ts_class = "user-timestamp" if msg["role"] == "user" else ""
            st.markdown(f'<div class="timestamp {ts_class}">{msg["timestamp"]}</div>', unsafe_allow_html=True)

# Display options buttons
if not st.session_state.first_message_sent:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("☐ Chat with sales", key="opt1", use_container_width=True):
            st.session_state.first_message_sent = True
            user_msg = "Chat with sales"
            now = datetime.now().strftime("%I:%M %p")
            st.session_state.messages.append({"role": "user", "content": user_msg, "timestamp": now})
            reply = call_openrouter(user_msg)
            st.session_state.messages.append({"role": "assistant", "content": reply, "timestamp": datetime.now().strftime("%I:%M %p")})
            st.rerun()
    with col2:
        if st.button("🗹 Book a demo", key="opt2", use_container_width=True):
            st.session_state.first_message_sent = True
            user_msg = "Book a demo"
            now = datetime.now().strftime("%I:%M %p")
            st.session_state.messages.append({"role": "user", "content": user_msg, "timestamp": now})
            reply = call_openrouter(user_msg)
            st.session_state.messages.append({"role": "assistant", "content": reply, "timestamp": datetime.now().strftime("%I:%M %p")})
            st.rerun()
    with col3:
        if st.button("❌ Get started for free", key="opt3", use_container_width=True):
            st.session_state.first_message_sent = True
            user_msg = "Get started for free"
            now = datetime.now().strftime("%I:%M %p")
            st.session_state.messages.append({"role": "user", "content": user_msg, "timestamp": now})
            reply = call_openrouter(user_msg)
            st.session_state.messages.append({"role": "assistant", "content": reply, "timestamp": datetime.now().strftime("%I:%M %p")})
            st.rerun()
    with col4:
        if st.button("☐ Get help with my account", key="opt4", use_container_width=True):
            st.session_state.first_message_sent = True
            user_msg = "Get help with my account"
            now = datetime.now().strftime("%I:%M %p")
            st.session_state.messages.append({"role": "user", "content": user_msg, "timestamp": now})
            reply = call_openrouter(user_msg)
            st.session_state.messages.append({"role": "assistant", "content": reply, "timestamp": datetime.now().strftime("%I:%M %p")})
            st.rerun()
    st.markdown("""
    <div class="disclaimer">
        HubSpot uses the information you provide to us to contact you about our relevant content, products, and services. Check out our <a href="#">privacy policy</a> here.
    </div>
    <div class="ai-warning">AI-generated content may be inaccurate.</div>
    """, unsafe_allow_html=True)

# Display chat input
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.first_message_sent = True
    now = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": now})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        st.markdown(f'<div class="timestamp user-timestamp">{now}</div>', unsafe_allow_html=True)
    reply = call_openrouter(prompt)
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(reply)
        st.markdown(f'<div class="timestamp">{datetime.now().strftime("%I:%M %p")}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": reply, "timestamp": datetime.now().strftime("%I:%M %p")})
    st.rerun()