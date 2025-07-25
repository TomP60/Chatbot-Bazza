import streamlit as st
from persona_config import get_persona_prompt
from rag_engine import get_response

# Optional: only if TTS used
try:
    from gtts import gTTS
    import os
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# --- App Setup ---
st.set_page_config(page_title="Talk to Bazza", page_icon="🦘")

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "full_log" not in st.session_state:
    st.session_state.full_log = []

# --- Sidebar Options ---
st.sidebar.header("⚙️ Settings")

book_option = st.sidebar.selectbox(
    "📚 Select Book/Topic",
    ["Excel Budgeting", "Australian Slang", "Periodic Table", "MySQL Workshop"]
)

# --- Book Thumbnails and Links ---
book_thumbnails = {
    "Excel Budgeting": {
        "image": "assets/excel_book_thumb.jpg",
        "link": "https://www.amazon.com/dp/B0FF377S6T"
    },
    "Australian Slang": {
        "image": "assets/slang_book_thumb.jpg",
        "link": "https://www.amazon.com/dp/B0DX7CQQNN"
    },
    "Periodic Table": {
        "image": "assets/periodic_book_thumb.jpg",
        "link": "https://www.amazon.com/dp/B0DYK9GP2V"
    },
    "MySQL Workshop": {
        "image": "assets/mysql_book_thumb.jpg",
        "link": "https://www.amazon.com/dp/B084T32T3B"
    }
}

# Show selected book thumbnail and link
if book_option in book_thumbnails:
    img_info = book_thumbnails[book_option]
    st.sidebar.image(img_info["image"], caption=f"{book_option}", use_container_width=True)
    st.sidebar.markdown(f"[📖 View on Amazon]({img_info['link']})", unsafe_allow_html=True)

persona_option = st.sidebar.selectbox(
    "🎭 Select Persona",
    ["Bazza (Aussie)", "Nerdy (Geek)", "Robot (Neutral)"]
)

pg_mode = st.sidebar.checkbox("🧺 Keep it clean? (PG Mode)", value=True)

# --- Heading & Persona ---
persona_name = persona_option.split()[0]
icon_map = {
    "Bazza": "🦘",
    "Nerdy": "🤓",
    "Robot": "🤖"
}
image_map = {
    "Bazza": "assets/bazza_thumb.jpg",
    "Nerdy": "assets/nerdy_thumb.jpg",
    "Robot": "assets/robot_thumb.jpg"
}

# Display title + image side by side
col1, col2 = st.columns([1, 8])
with col1:
    st.image(image_map[persona_name], width=64)
with col2:
    st.title(f"Meet {persona_name} – Your AI Mate {icon_map.get(persona_name)}")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About This App")
st.sidebar.markdown(
    "🦘 **Bazza Chat** is an interactive assistant trained on selected books published by **PetiteKat Press**.\n\n"
    "Ask questions, learn slang, explore Excel or MySQL — all with a bit of personality.\n\n"
    "👨‍💻 **Written by Thomas W. Pettit**  \n"
    "📘 Visit: [PetiteKatPress.com](https://www.petitekatpress.com)  \n"
    f"🛠️ Version: `v1.0.0`  \n"
)


# --- Input ---
st.markdown("Ask a question or have a yarn below:")
user_input = st.text_input("💬 You:")

# --- Generate Response ---
if user_input:
    with st.spinner(f"{persona_name}’s thinking..."):
        # Memory jogger: up to 5 previous exchanges
        memory_context = "\n\n".join(
            f"Q: {q}\nA: {a}" for q, a in st.session_state.chat_history[-5:]
        )
        system_prompt = get_persona_prompt(persona_option, book_option) + "\n" + memory_context
        response = get_response(user_input, system_prompt, book_option, pg_mode=pg_mode)

    # --- Save to session memory (view) and full log (file) ---
    st.session_state.chat_history.append((user_input, response))
    if len(st.session_state.chat_history) > 5:
        st.session_state.chat_history.pop(0)
    st.session_state.full_log.append((user_input, response))

    # --- Display Response ---
    st.markdown(f"**{persona_name}**: {response}")

    # --- TTS ---
    if TTS_AVAILABLE:
        speaker_label = {
            "Bazza": "🔊 Hear Bazza Say It",
            "Nerdy": "🔊 Hear Nerdy Explain It",
            "Robot": "🔊 Hear Robot Response"
        }.get(persona_name, "🔊 Hear It")

        if st.button(speaker_label):
            tts = gTTS(text=response, lang='en')
            tts.save("bazza.mp3")
            audio_file = open("bazza.mp3", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")

# --- Show Session History (short memory) ---
if st.session_state.chat_history:
    with st.expander("📜 View Conversation History"):
        for i, (q, a) in enumerate(st.session_state.chat_history, 1):
            st.markdown(f"**Q{i}:** {q}")
            st.markdown(f"**A{i}:** {a}")

# --- Full Log Download ---
if st.session_state.full_log:
    if st.button("📥 Download Full Conversation (.txt)"):
        full_text = "\n\n".join(
            f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(st.session_state.full_log)
        )
        with open("bazza_full_log.txt", "w", encoding="utf-8") as f:
            f.write(full_text)
        with open("bazza_full_log.txt", "rb") as f:
            st.download_button("Click to download", f, file_name="bazza_chat_history.txt")
