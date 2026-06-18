"""
Login page - Check if user has participated before.
"""
import streamlit as st
from utils.data_persistence import user_exists

def show():
    """Display the login screen with welcome message."""
    # Welcome message at the top
    st.markdown("""
    ## Willkommen!

Vielen Dank für Ihre Teilnahme!

Wenn Sie bereits teilgenommen haben, geben Sie bitte unten Ihre Benutzer-ID ein, um direkt dort weiterzumachen, wo Sie aufgehört haben.

Wenn Sie neu teilnehmen, erhalten Sie zunächst weitere Informationen zur Studie und müssen Ihre Einwilligung geben, bevor Sie fortfahren können.

Anschließend füllen Sie einen kurzen demografischen Fragebogen aus. Die im Fragebogen angegebenen Informationen werden nicht mit Ihrer Identität verknüpft und sind sehr wichtig, um die Studienergebnisse einordnen zu können.

Zum Schluss erhalten Sie  **vor Beginn der Hauptaufgabe 2 Übungsdurchgänge** um sich mit der Umfrage vertraut zu machen!

    ### Wichtige Hinweise:

    - Bitte führen Sie die Bewertungen in einer ruhigen Umgebung ohne Ablenkungen durch
    - Alle Daten werden mithilfe einer generierten Benutzer-ID anonymisiert

    ---
    """)

    st.markdown("")  # Spacing

    # Login section
    st.markdown("### Haben Sie bereits an dieser Studie teilgenommen?")

    # Radio button for Yes/No
    participated = st.radio(
        "Select one:",
        options=["Nein, dies ist meine erste Teilnahme.", "Ja, ich habe bereits teilgenommen."],
        key="participated_radio",
        label_visibility="collapsed"
    )

    st.markdown("")  # Spacing

    # If user selected "Yes", show user ID input
    if participated == "Yes, I have participated before":
        st.markdown("### Bitte geben Sie Ihre Benutzer-ID ein")

        user_id_input = st.text_input(
            "User ID:",
            key="user_id_input",
            placeholder="Enter your user ID (e.g., ABCD12 or giha3042)",
            help="Ihre Benutzer-ID wurde Ihnen nach dem Ausfüllen des Fragebogens angezeigt"
        ).strip()

        # Check if user ID exists
        if user_id_input:
            if user_exists(user_id_input):
                st.success(f"✓ User ID '{user_id_input}' found!")
                st.session_state.user_id_valid = True
                # Store the user ID as entered (preserve original case)
                st.session_state.validated_user_id = user_id_input
            else:
                st.error("⚠️ User ID not found. Please check your ID or select 'No' if this is your first time.")
                st.info("💡 If you cannot remember your user ID, please reach out to the study administration.")
                st.session_state.user_id_valid = False
        else:
            st.session_state.user_id_valid = False

    # Navigation buttons
    st.markdown("")
    st.markdown("")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("Next ▶️", use_container_width=True, type="primary"):
            # Validation
            if participated == "Yes, I have participated before":
                if not user_id_input:
                    st.error("Bitte geben Sie Ihre Benutzer-ID ein")
                    st.info("💡 Wenn Sie sich nicht an Ihre Benutzer-ID erinnern können, wenden Sie sich bitte an die Studienleitung.")
                    st.stop()
                elif not st.session_state.get('user_id_valid', False):
                    st.error("Benutzer-ID nicht gefunden. Bitte überprüfen Sie Ihre ID.")
                    st.info("💡 Wenn Sie sich nicht an Ihre Benutzer-ID erinnern können, wenden Sie sich bitte an die Studienleitung.")
                    st.stop()
                else:
                    # Valid returning user - use the validated ID with original case
                    st.session_state.user.user_id = st.session_state.get('validated_user_id', user_id_input)

                    # Check if familiarization is enabled
                    config = st.session_state.config
                    enable_familiarization = config.get('settings', {}).get('enable_familiarization', True)

                    if enable_familiarization:
                        st.session_state.page = 'pre_familiarization'
                    else:
                        st.session_state.page = 'videoplayer'

                    st.rerun()
            else:
                # New user - go to consent page
                st.session_state.page = 'consent'
                st.rerun()
