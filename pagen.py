import streamlit as st
import openai
import time
from PIL import Image  # For displaying uploaded images if needed
import os
import dotenv
dotenv.load_dotenv()

assistant_id = "asst_zNdomFjIbZWnqyI2IDv7lbTM"
client = openai


if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

st.set_page_config(page_title="KIDD_paGen", page_icon=":robot_face:")


if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

st.title("Pre-Assessment Question Generator")
st.write("Input a standard, learning goals, and document to reference.")

if st.sidebar.button("Exit Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.thread_id = None

if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o"
    if "messages" not in st.session_state:
        st.session_state.messages = []

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

        # Display the assembled prompt in the chat and add it to session state
        st.session_state.messages.append({"role": "user", "content": prompt_text})
        with st.chat_message("user"):
            st.markdown(prompt_text)

        # Send the assembled prompt to OpenAI
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt_text
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions=
            "# CONTEXT # I am a curriculum writer authoring questions to check my student's readiness for an upcoming unit. # OBJECTIVE # I am going to provide you  - a set of checkpoint questions attached as an image,  - the math standard(s) being addressed - the learning goals for a section - Which PDF attachment to refer Using these as the goal I want my students to achieve, I want you to review the attached PDF in your attached file for additional research before creating a list of skills that my students would need to be successful on these proble Based on that list of skills I want you to then draft 5 questions that I could use to assess my students' readiness for this sections of stu \# STYLE # I want this to be in the style of an education assessm \# TONE #  Educational and professional, but appropriate for students in the specified grade lev \# AUDIENCE # Grade 4 stud \# RESPONSE # Identified skills you used to create the questions and 5 questions in a markdown li 2 questions should be multiple choice, and 3 should be open respons With each question provide a justification for how they can help teachers assess a student’s readiness for the content presented in this secti \###"
        )
        
        # Polling for the completion of the assistant's response
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.markdown(message.content[0].text.value)

else:
    st.write("Click 'Start Chat' to begin.")
