import streamlit as st
from groq import Groq
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image
from dotenv import load_dotenv

# API Key load karne ke liye (Local testing ke liye .env file use karein)
load_dotenv()

# --- Page Configuration ---
st.set_page_config(page_title="Math Slay AI", layout="wide")

# --- Custom CSS for Midnight Theme ---
st.markdown("""
    <style>
    .stApp { background-color: #0d3861; color: white; }
    .stTextInput>div>div>input { background-color: #0a2a47; color: white; border: 1px solid #8a2be2; }
    .stChatMessage { background-color: #0a2a47 !important; border-radius: 15px; border: 1px solid #4b0082 !important; margin-bottom: 10px; }
    div.stButton > button {
        background: linear-gradient(45deg, #8a2be2, #00d4ff);
        color: white; border: none; border-radius: 8px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Graph Logic ---
def generate_graph(problem_text):
    try:
        # GitHub/Streamlit Cloud par Secrets mein GROQ_API_KEY hona chahiye
        api_key = os.getenv('GROQ_API_KEY')
        client = Groq(api_key=api_key)
        
        graph_prompt = f"Convert to Python numpy expression for plotting: '{problem_text}'. Return ONLY the expression like 'x**2'. No text."
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": graph_prompt}]).choices[0].message.content.strip()
        res = res.replace('`', '').replace('python', '').strip()
        
        x = np.linspace(-10, 10, 500)
        safe_env = {"np": np, "x": x, "sin": np.sin, "cos": np.cos, "tan": np.tan, "sqrt": np.sqrt, "log": np.log, "exp": np.exp}
        y = eval(res.replace('^', '**'), {"__builtins__": None}, safe_env)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#0d3861')
        ax.set_facecolor('#0a2a47')
        plt.axhline(0, color='white', linewidth=1.5, alpha=0.7)
        plt.axvline(0, color='white', linewidth=1.5, alpha=0.7)
        plt.plot(x, y, color="#00d4ff", linewidth=3)
        plt.grid(True, alpha=0.1)
        plt.tick_params(colors='white')
        for spine in ax.spines.values(): spine.set_color('white')
        
        return fig
    except:
        return None

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar ---
with st.sidebar:
    st.title("🌌 Math Slay Controls")
    category = st.selectbox("Realm", ["Mathematics", "Science", "Finance"])
    st.write("---")
    st.write("### Quick Symbols")
    symbols = ["√", "π", "^", "∫", "log", "sin", "cos", "tan"]
    # Symbols display (Streamlit buttons don't easily insert text into chat_input, 
    # but we show them as a reference)
    cols = st.columns(2)
    for i, sym in enumerate(symbols):
        cols[i % 2].button(sym, disabled=True)
    
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# --- Main App ---
st.title("🌌 MATH SLAY: STREAMLIT FEED")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "graph" in message:
            st.pyplot(message["graph"])

# Chat Input
if prompt := st.chat_input("Enter your math problem..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Solve logic
    try:
        api_key = os.getenv('GROQ_API_KEY')
        client = Groq(api_key=api_key)
        
        with st.spinner("AI is thinking..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[
                    {"role": "system", "content": f"You are a GenZ expert in {category}. Solve step-by-step using LaTeX."},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = completion.choices[0].message.content
            fig = generate_graph(prompt)
            
            # Prepare assistant response
            full_res = {"role": "assistant", "content": answer}
            if fig:
                full_res["graph"] = fig
            
            st.session_state.messages.append(full_res)
            
            # Display current response
            with st.chat_message("assistant"):
                st.markdown(answer)
                if fig:
                    st.pyplot(fig)
                    
    except Exception as e:
        st.error(f"Error: {str(e)}")
