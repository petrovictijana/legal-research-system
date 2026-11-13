
def apply_styles():
    import streamlit as st

    st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&family=Material+Symbols+Rounded" rel="stylesheet">

        <style>
        :root {
            --navy: #172B45;
            --burgundy: #8C2938;
            --background: #F5F7FA;
            --text: #263D5D;
            --muted: #7184A2;
            --border: #CCD7E7;
        }

        /* Global */

        .stApp {
            background: var(--background);
            font-family: 'DM Sans', sans-serif;
        }

        .block-container {
            max-width: 1050px;
            padding-top: 3rem;
            padding-bottom: 2rem;
        }

        /* Welcome section */

        .welcome-section {
            text-align: center;
            padding: 3rem 0 1.5rem;
            position: relative;
            z-index: 1;
        }

        .welcome-section::after {
            content: "§";
            position: fixed;
            right: -20px;
            top: 100px;
            font-family: 'Playfair Display', serif;
            font-size: 570px;
            line-height: 1;
            color: #E8EDF4;
            opacity: 0.65;
            z-index: -1;
            pointer-events: none;
        }

        .hero-icon {
            width: 86px;
            height: 86px;
            margin: 0 auto 22px;
            background: var(--navy);
            border-radius: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 20px rgba(23, 43, 69, 0.12);
        }

        .hero-icon .material-symbols-rounded {
            color: white;
            font-size: 43px;
            line-height: 1;
        }

        .welcome-section .welcome-title {
            font-family: 'Playfair Display', serif;
            color: var(--navy);
            font-size: clamp(34px, 4vw, 54px);
            font-weight: 700;
            line-height: 1.2;
            margin: 0 0 22px;
        }

        .welcome-section .welcome-description {
            color: #596D8C;
            font-family: 'DM Sans', sans-serif;
            font-size: 21px;
            font-weight: 400;
            line-height: 1.8;
            max-width: 720px;
            margin: 0 auto;
        }

        .welcome-section .examples-heading {
            text-align: left;
            color: #657A99;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 1.7px;
            margin-top: 43px;
            margin-bottom: 20px;
        }

        /* Example question cards */

        [class*="st-key-example_"] {
            position: relative;
            z-index: 1;
        }

        [class*="st-key-example_"] button {
            min-height: 88px;
            border: none;
            border-radius: 20px;
            background: #EDF1F7;
            color: var(--navy);
            text-align: left;
            font-family: 'DM Sans', sans-serif;
            font-size: 16px;
            font-weight: 500;
            padding: 17px 22px;
            transition: all 0.2s ease;
        }

        [class*="st-key-example_"] button:hover {
            background: #E3EAF4;
            color: var(--navy);
            transform: translateY(-2px);
        }

        [class*="st-key-example_"] button p {
            line-height: 1.6;
        }

        /* Question input */

        [data-testid="stForm"] {
            position: relative;
            z-index: 1;
            margin-top: 48px;
            padding: 13px 16px;
            background: #FFFFFF;
            border: 1.5px solid var(--border);
            border-radius: 19px;
            box-shadow: 0 3px 12px rgba(23, 43, 69, 0.03);
        }

        [data-testid="stForm"] [data-testid="stTextInput"] {
            margin-bottom: 0;
        }

        [data-testid="stForm"] input {
            background: transparent;
            border: none;
            box-shadow: none;
            color: var(--navy);
            font-size: 17px;
            min-height: 48px;
        }

        [data-testid="stForm"] input:focus {
            border: none;
            box-shadow: none;
        }

        [data-testid="stForm"] input::placeholder {
            color: #9AACC9;
        }

        [data-testid="stForm"] button {
            min-height: 50px;
            background: var(--burgundy);
            color: white;
            border: none;
            border-radius: 11px;
            font-size: 25px;
            transition: background 0.2s ease;
        }

        [data-testid="stForm"] button:hover {
            background: #73212E;
            color: white;
        }

        /* Chat */

        [data-testid="stChatMessage"] {
            position: relative;
            z-index: 1;
            border-radius: 16px;
            padding: 18px;
        }

        /* Disclaimer */

        .disclaimer {
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            color: #8295B2;
            font-size: 13px;
            text-align: center;
            margin-top: 20px;
        }

        .disclaimer .material-symbols-rounded {
            font-size: 20px;
        }

        .disclaimer a {
            color: var(--burgundy);
            text-decoration: underline;
        }

        /* Responsive */

        @media (max-width: 700px) {
            .block-container {
                padding: 1.5rem 1rem;
            }

            .welcome-section {
                padding-top: 2rem;
            }

            .welcome-section .welcome-title {
                font-size: 34px;
            }

            .welcome-section .welcome-description {
                font-size: 16px;
                line-height: 1.7;
            }

            .welcome-section::after {
                display: none;
            }

            .hero-icon {
                width: 70px;
                height: 70px;
                border-radius: 23px;
            }

            .examples-heading {
                margin-top: 30px;
            }

            [class*="st-key-example_"] button {
                font-size: 14px;
                padding: 14px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )
