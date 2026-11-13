
import logging
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.styles import apply_styles
from app.components import (
    render_welcome,
    render_question_input,
    render_sources,
    render_disclaimer
)
from orchestration.query_pipeline import generate_answer


logger = logging.getLogger(__name__)


st.set_page_config(
    page_title="Правнислав",
    page_icon="⚖️",
    layout="centered"
)


# Apply application styles
apply_styles()


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []


# Welcome screen
if not st.session_state.messages:
    render_welcome()


# Conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            render_sources(message.get("sources", []))


# Question input
question = render_question_input()

pending_question = st.session_state.pop(
    "pending_question",
    None
)

if pending_question:
    question = pending_question


# Process question
if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Правнислав припрема одговор..."):
            try:
                result = generate_answer(query=question)

                answer = result["answer"]
                sources = result["sources"]

                st.markdown(answer)
                render_sources(sources)

            except Exception:
                logger.exception("RAG pipeline execution failed.")

                answer = (
                    "Дошло је до грешке приликом обраде питања. "
                    "Покушајте поново."
                )
                sources = []

                st.error(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })

    st.rerun()


# Disclaimer
render_disclaimer()
