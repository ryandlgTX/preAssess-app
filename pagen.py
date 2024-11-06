import streamlit as st
import openai
import time
from PIL import Image  # For displaying uploaded images if needed
import os
import dotenv
dotenv.load_dotenv()

assistant_id = "asst_zNdomFjIbZWnqyI2IDv7lbTM"
openai.api_key = os.getenv("OPENAI_API_KEY")

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="KIDD_paGen", page_icon=":robot_face:")

if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    st.session_state.messages.append({"role": "system", "content": "You are an assistant that generates pre-assessment questions for students."})

st.title("Pre-Assessment Question Generator")
st.write("Input a standard, learning goals, and document to reference.")

if st.sidebar.button("Exit Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state

if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4"
    
    # Two-column layout for Standards and Learning Goals input
    col1, col2 = st.columns(2)
    with col1:
        standard = st.text_area("Enter Standard:", height=100)
    with col2:
        goals = st.text_area("Enter Learning Goals:", height=100)

    # Dropdown menu for reference document selection
    reference = st.selectbox(
        "Select a reference document:",
        ["3–5 Progression on Number and Operations—Fractions.pdf", "3-5 NBT Progressions.pdf"]
    )

    # Image uploader for multiple images
    uploaded_images = st.file_uploader("Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    # Submit button to send data to OpenAI
    if st.button("Submit"):
        # Assemble the final prompt with standards, goals, reference, and images
        prompt_text = f">>>Standards: {standard} >>>Learning Goals: {goals} >>>Reference: {reference}\n"
        
        # Add the uploaded images information (images can be processed further if needed)
        if uploaded_images:
            for img in uploaded_images:
                prompt_text += f"- Attached image: {img.name}\n"

        # Display the assembled prompt for logging/debugging
        st.write("**Full Prompt Being Sent:**")
        st.text(prompt_text)  # Displays the full prompt text in the Streamlit app for review

        # Append user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt_text})
        with st.chat_message("user"):
            st.markdown(prompt_text)

        # Send the assembled prompt to OpenAI
        response = openai.ChatCompletion.create(
            model=st.session_state.openai_model,
            messages=st.session_state.messages
        )

        # Process and display assistant's response
        assistant_message = response.choices[0].message['content']
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        with st.chat_message("assistant"):
            st.markdown(assistant_message)

else:
    st.write("Click 'Start Chat' to begin.")
