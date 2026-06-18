"""
Welcome page - Initial instructions screen.
"""
import streamlit as st

def show():
    """Display the welcome screen."""
    #st.title("⚽ Creativity Rating App")

    st.markdown("""
    ## Willkommen!

Sie erhalten in Kürze spezifische Informationen zur Studie. Hier finden Sie eine Übersicht über die einzelnen Schritte:

    ### Anweisungen:

    1. **Login**: Zunächst geben Sie an, ob Sie bereits teilgenommen haben
    2. **Fragebogen**: Neue Teilnehmende füllen einen kurzen demografischen Fragebogen aus
    3. **Eingewöhnung**: Sie durchlaufen Übungsdurchgänge, um sich mit der Bewertungsoberfläche vertraut zu machen
    4. **Bewertung**: Sie sehen Bilder und bewerten verschiedene Aspekte jedes Bildes

    ### Wichtige Hinweise:

    - Bitte führen Sie die Bewertungen in einer ruhigen Umgebung ohne Ablenkungen durch
    - Alle Daten werden mithilfe einer generierten Benutzer-ID anonymisiert

    ---

    **Bereit zu beginnen?** Klicken Sie auf die Schaltfläche unten, um fortzufahren.
    """)

    st.markdown("")  # Spacing

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("▶️ Next", use_container_width=True, type="primary"):
            st.session_state.page = 'login'
            st.rerun()
