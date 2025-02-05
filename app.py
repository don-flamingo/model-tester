import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY") 

SYSTEM_PROMPT = """
# GOAL
Twoim celem jest dowiedzenie się tego czego użytkownik chce się nauczyć i w jaki sposób.

# CONTEXT
Jesteś częścią aplikacji mobilnej, która jest osobistym nauczycielem i przeprowadza szkolenie w tej aplikacji. Aplikacja tworzy spersonalizowane kursy na podstawie podanych preferencji (samo tworzenie kursów jest zadaniem innego agenta). Aktualnie aplikacja wspiera tylko kursy w formie tekstowej.

# INSTRUCTION
- Zadawaj pytania pojedynczo.
- Zadaj nie więcej niż 4 pytania, ale możesz zakończyć wcześniej jeśli zyskasz wystarczającą liczbę informacji.
- Dopytaj się o ilość czasu jaki użytkownik chce poświęcić codziennie na naukę.
- Dowiedz się jakie doświadczenie ma użytkownik w danym temacie.
- Na końcu stwórz podsumowanie (na jego podstawie będzie wygenerowany kurs) i zapytaj się użytkownika czy chce coś jeszcze dodać/doprecyzować, albo przejść do kolejnych pytań, aby kurs był bardziej spersonalizowany.
"""

def call_model(model, role):
    try:
        conversation_history = st.session_state.get("conversation", [])
        messages = [{"role": role, "content": SYSTEM_PROMPT}] + conversation_history
        response = openai.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def call_gpt4o():
    return call_model("gpt-4o", "system")

def call_gpt4o_mini():
    return call_model("gpt-4o-mini", "system")

def call_o3_mini():
    return call_model("o3-mini", "developer")

def main():
    st.title("Multi-Model Chat Interface")
    st.write("Czego chcesz się nauczyć?")

    # Sidebar for model selection and clearing conversation
    st.sidebar.header("Model Selection")
    model_choice = st.sidebar.selectbox("Select the model to chat with:", 
                                        ["gpt-4o-mini", "gpt-4o", "o3-mini"])
    
    if st.sidebar.button("Clear Chat"):
        st.session_state.conversation = []

    # Initialize conversation session state if not already present
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display conversation history
    st.markdown("## Conversation")
    for message in st.session_state.conversation:
        if message["role"] == "user":
            st.markdown(f"**User:** {message['content']}")
        else:
            st.markdown(f"**Model:** {message['content']}")

    # Input form for new message
    with st.form(key="chat_form", clear_on_submit=True):
        user_message = st.text_input("Your message:")
        submit_button = st.form_submit_button("Send")

    if submit_button and user_message.strip() != "":
        # Add user message to conversation history
        st.session_state.conversation.append({"role": "user", "content": user_message})
        with st.spinner("Getting response..."):
            if model_choice == "gpt-4o":
                response = call_gpt4o()
            elif model_choice == "gpt-4o-mini":
                response = call_gpt4o_mini()
            elif model_choice == "o3-mini":
                response = call_o3_mini()
            else:
                response = "Invalid model selection."
        # Append the model's response to the conversation
        st.session_state.conversation.append({"role": "assistant", "content": response})
        st.rerun()

if __name__ == '__main__':
    main() 