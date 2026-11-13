
import streamlit as st


EXAMPLE_QUESTIONS = [
    {
        "text": "Која су моја права приликом отказа уговора о раду?",
        "icon": ":material/description:"
    },
    {
        "text": "Како се региструје привредно друштво у Србији?",
        "icon": ":material/home_work:"
    },
    {
        "text": "Која су права родитеља на породиљско одсуство?",
        "icon": ":material/groups:"
    },
    {
        "text": "Када је обавезно имати зимске гуме на возилу?",
        "icon": ":material/directions_car:"
    }
]


def render_welcome():
    st.markdown(
        """
        <div class="welcome-section">

            <div class="hero-icon">
                <span class="material-symbols-rounded">chat</span>
            </div>

            <div class="welcome-title">
                Питајте Правнислава
            </div>

            <div class="welcome-description">
                Поставите питање о законима и добијте јасне одговоре
                засноване на званичним правним документима.
            </div>

            <div class="examples-heading">
                ПРИМЕРИ ПИТАЊА
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2, gap="medium")

    for index, example in enumerate(EXAMPLE_QUESTIONS):
        column = col1 if index % 2 == 0 else col2

        with column:
            if st.button(
                f'{example["icon"]} {example["text"]}  →',
                key=f"example_{index}",
                use_container_width=True
            ):
                st.session_state["pending_question"] = example["text"]
                st.rerun()


def render_question_input():
    with st.form("question_form", clear_on_submit=True):
        col1, col2 = st.columns([0.90, 0.10], gap="small")

        with col1:
            question = st.text_input(
                "Питање",
                placeholder="Унесите ваше питање овде...",
                label_visibility="collapsed"
            )

        with col2:
            submitted = st.form_submit_button(
                "➜",
                use_container_width=True
            )

    if submitted and question.strip():
        return question.strip()

    return None


def render_disclaimer():
    st.markdown(
        """
        <div class="disclaimer">
            <span class="material-symbols-rounded">info</span>
            <span>
                Одговори су генерисани уз помоћ вештачке интелигенције
                и засновани на доступним правним изворима.
                <a href="#" target="_self">Сазнајте више.</a>
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_sources(sources: list[dict]):
    if not sources:
        return

    with st.expander("Правни извори", expanded=False):
        for source in sources:
            document_title = source.get(
                "document_title",
                "Непознат документ"
            )
            article_number = source.get("article_number")
            content = source.get("content", "")

            st.markdown(f"**{document_title}**")

            if article_number is not None:
                st.caption(f"Члан {article_number}")

            if content:
                with st.expander("Прикажи садржај члана"):
                    st.markdown(content)

            st.divider()
