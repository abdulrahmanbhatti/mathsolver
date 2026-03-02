import streamlit as st
from groq import Groq
import matplotlib.pyplot as plt
import numpy as np
import os

st.set_page_config(page_title="🌌 MATH SLAY", layout="wide")

# ---------- Custom Styling ----------
st.markdown("""
<style>
body {background-color: #0d3861;}
.stApp {background-color: #0d3861; color: white;}
button[kind="primary"] {
    background: linear-gradient(45deg, #8a2be2, #00d4ff);
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.title("🔮 Realm")
category = st.sidebar.selectbox("Choose Category", ["Mathematics", "Science", "Finance"])

if st.sidebar.button("🔄 New Chat"):
    st.session_state.history = []

# ---------- Session State ----------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- Title ----------
st.markdown("<h1 style='text-align:center;'>🌌 MATH SLAY: ALL-IN-ONE FEED</h1>", unsafe_allow_html=True)

# ---------- User Input ----------
problem = st.text_input("Enter your problem")

# ---------- Solve Button ----------
if st.button("Solve Everything ✨") and problem.strip():

    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)

    # ----- Get AI Solution -----
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"Expert in {category}. Use LaTeX and solve step-by-step."},
            {"role": "user", "content": problem}
        ]
    )

    answer = completion.choices[0].message.content

    # Save history
    st.session_state.history.append(("user", problem))
    st.session_state.history.append(("bot", answer))

    # ----- Graph Generation -----
    try:
        graph_prompt = f"Convert to Python numpy expression: '{problem}'. Return ONLY x**2 style code."
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": graph_prompt}]
        ).choices[0].message.content.strip()

        res = res.replace('`', '').replace('python', '').strip()

        x = np.linspace(-10, 10, 500)
        safe_env = {
            "np": np, "x": x,
            "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "sqrt": np.sqrt, "log": np.log, "exp": np.exp
        }

        y = eval(res.replace("^", "**"), {"__builtins__": None}, safe_env)

        fig, ax = plt.subplots()
        ax.axhline(0)
        ax.axvline(0)
        ax.plot(x, y)
        st.pyplot(fig)

    except:
        pass

# ---------- Chat Display ----------
for role, msg in st.session_state.history:
    if role == "user":
        with st.chat_message("user"):
            st.markdown(msg)
    else:
        with st.chat_message("assistant"):
            st.markdown(msg)
