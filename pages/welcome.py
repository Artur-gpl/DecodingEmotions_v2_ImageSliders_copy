"""
Welcome page - Initial instructions screen.
"""
import streamlit as st

def show():
    """Display the welcome screen."""
    #st.title("⚽ Creativity Rating App")

    st.markdown("""
    ## Welcome!

    You will be receiving specific information regarding the study soon. Here you will find an overview of the steps involved in the study:

    ### Instructions:

    1. **Login**: First, you'll indicate whether you've participated before
    2. **Questionnaire**: New users will complete a brief demographic questionnaire
    3. **Familiarization**: You'll go through practice trials to get used to the rating interface
    4. **Rating**: You'll watch images and rate various aspects of each image

    ### Important Notes:

    - Please complete ratings in a quiet environment without distractions
    - All data is anonymized using a generated user ID

    ---

    **Ready to begin?** Click the button below to proceed.
    """)

    st.markdown("")  # Spacing

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("▶️ Next", use_container_width=True, type="primary"):
            st.session_state.page = 'login'
            st.rerun()
