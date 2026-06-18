"""
Consent page - Participant information and consent form.
"""
import streamlit as st
import os

def show():
    """Display the consent screen."""
    st.title("📋 Participant Information and Consent")

    st.markdown("---")

    # Get consent PDF path from config
    config = st.session_state.config
    consent_pdf_path = config.get('paths', {}).get('consent_pdf_path', None)

    # Download button for consent PDF
    if consent_pdf_path and os.path.exists(consent_pdf_path):
        st.markdown("""
        Unser Forschungsprojekt befasst sich mit der Frage, inwiefern Körpersignale und Gesichtssignale die Einschätzung von Wettkampfergebnissen sowie die Erkennung von Emotionen in sportlichen Kontexten beeinflussen.

        Sie haben das Recht, jederzeit Fragen zu stellen und die Untersuchung ohne Gefährdung oder sonstige Nachteile für Sie jederzeit abzubrechen. Die Teilnahme ist freiwillig.
Die Deutsche Sporthochschule Köln hat keine Probandenversicherung für dieses Vorhaben abgeschlossen.

Eine Haftung für Sach- und Personenschäden gegen die Deutsche Sporthochschule Köln und ihre Mitarbeiter:innen ist ausgeschlossen, es sei denn, der entstandene Schaden beruht auf Vorsatz oder grober Fahrlässigkeit.
Einwilligung zur Verarbeitung personenbezogener Daten
Eine Verarbeitung Ihrer personenbezogenen Daten im Rahmen des oben genannten Forschungsprojektes ist nur mit Ihrer ausdrücklichen und freiwilligen Einwilligung möglich.

Hiermit willigen Sie ausdrücklich ein, dass die Deutsche Sporthochschule Köln zum Zwecke des Forschungsprojektes folgende Daten von Ihnen erheben, speichern und nutzen darf: Antworten im Online-Fragebogen sowie allgemeine demografische Angaben. Eine Veröffentlichung der Daten erfolgt nur in anonymisierter Form, also ohne die Möglichkeit, einen Rückschluss auf Ihre Person zu ziehen.
Es ist nicht beabsichtigt, Daten an Dritte weiterzugeben.

Sie können diese Einwilligung jederzeit mit Wirkung für die Zukunft ohne Nachteile widerrufen. In diesem Falle werden Ihre personenbezogenen Daten, soweit eine Zuordnung möglich ist, unverzüglich gelöscht. Durch den Widerruf der Einwilligung wird die Rechtmäßigkeit der aufgrund der Einwilligung bis zum Widerruf erfolgten Verarbeitung nicht berührt. Eine weitere Teilnahme am Forschungsprojekt ist nur bei Vorliegen der Einwilligung möglich.
Die Verwendung dieser Daten erfolgt ausschließlich nach den gesetzlichen Bestimmungen, insbesondere der DSGVO, und entsprechend dieser Erklärung.

        """)

        


    # Consent Section
    st.markdown("## Consent Declaration")

    # Consent checkbox
    consent_given = st.checkbox(
        "**I confirm that**",
        key="consent_checkbox"
    )

    st.markdown("""

                1. Ich habe die oben stehenden Teilnehmerinformationen gelesen und verstanden
                2. Ich nehme freiwillig an dieser Forschungsstudie teil
                3. Meine Daten können anonym zu Forschungszwecken genutzt werden
                4. Ich bin mindestens 18 Jahre alt
                """)
    
    st.markdown("")
    st.markdown("")

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("◀️ Back", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()

    with col3:
        if st.button("Next ▶️", use_container_width=True, type="primary"):
            if not consent_given:
                st.error("⚠️ You must provide your consent to proceed with the study.")
                st.stop()
            else:
                # Store consent in session state with timestamp
                from datetime import datetime
                st.session_state.consent_given = True
                st.session_state.consent_timestamp = datetime.now().isoformat(timespec='seconds')
                st.session_state.page = 'questionnaire'
                st.rerun()
