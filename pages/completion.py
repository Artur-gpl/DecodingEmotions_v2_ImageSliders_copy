"""
Completion page - Shows results after all videos are rated.
Displays completion message and win/loss prediction accuracy with confusion matrix.
"""
import streamlit as st
import pandas as pd


def calculate_accuracy_stats(session_ratings, metadata):
    """
    Calculate win/loss prediction accuracy for the current session.

    Parameters:
    - session_ratings: Dictionary {video_id: win_or_loss_prediction} from current session
    - metadata: DataFrame with 'id' and 'WinLoss' columns

    Returns:
    - Dictionary with accuracy statistics and confusion matrix data, or dict with 'error' key
    """
    if not session_ratings:
        return {'error': 'No ratings found in current session'}

    # Match ratings with ground truth from metadata
    confusion_matrix = {
        'true_win': 0,   # Predicted win, actual win
        'false_win': 0,  # Predicted win, actual loss
        'true_loss': 0,  # Predicted loss, actual loss
        'false_loss': 0  # Predicted loss, actual win
    }

    total_predictions = 0
    skipped_no_prediction = 0
    skipped_no_metadata = 0

    for video_id, prediction in session_ratings.items():
        # Skip if no prediction
        if prediction is None or prediction == '':
            skipped_no_prediction += 1
            continue

        # Find ground truth in metadata
        metadata_row = metadata[metadata['id'] == video_id]
        if metadata_row.empty:
            skipped_no_metadata += 1
            continue

        ground_truth = metadata_row.iloc[0]['WinLoss']

        # Normalize for comparison (case-insensitive)
        prediction_lower = str(prediction).lower()
        ground_truth_lower = str(ground_truth).lower()

        total_predictions += 1

        # Update confusion matrix
        if prediction_lower == 'win' and ground_truth_lower == 'win':
            confusion_matrix['true_win'] += 1
        elif prediction_lower == 'win' and ground_truth_lower == 'loss':
            confusion_matrix['false_win'] += 1
        elif prediction_lower == 'loss' and ground_truth_lower == 'loss':
            confusion_matrix['true_loss'] += 1
        elif prediction_lower == 'loss' and ground_truth_lower == 'win':
            confusion_matrix['false_loss'] += 1

    if total_predictions == 0:
        return {'error': f'No valid predictions matched with metadata (skipped: {skipped_no_prediction} empty, {skipped_no_metadata} missing metadata)'}

    # Calculate accuracy
    correct = confusion_matrix['true_win'] + confusion_matrix['true_loss']
    accuracy = (correct / total_predictions) * 100

    return {
        'confusion_matrix': confusion_matrix,
        'total_predictions': total_predictions,
        'correct_predictions': correct,
        'accuracy': accuracy
    }


def show():
    """Display the completion screen with accuracy statistics."""
    metadata = st.session_state.get('metadata', pd.DataFrame())
    session_ratings = st.session_state.get('session_ratings', {})

    st.title("🎉 All Done!")

    st.success("""
    ### Thank you for your participation!

    You have completed rating all available images.

    Below, you see how well you performed in predicting the competition outcomes based on the images.
    """)

    # Calculate and display accuracy statistics
    if not metadata.empty and 'WinLoss' in metadata.columns and session_ratings:
        stats = calculate_accuracy_stats(session_ratings, metadata)

        if stats and 'error' not in stats:
            st.markdown("---")
            st.subheader("📊 Your Win/Loss Prediction Accuracy")

            # Display overall accuracy
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            with col2:
                st.metric(
                    label="Overall Accuracy",
                    value=f"{stats['accuracy']:.1f}%",
                    delta=f"{stats['correct_predictions']}/{stats['total_predictions']} correct"
                )

            with col3:
                # Display confusion matrix
                st.markdown("#### Detailed Breakdown")

                cm = stats['confusion_matrix']

            # Create a visual confusion matrix using columns
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Predicted: Win**")
                    st.info(f"✅ **True Win**: {cm['true_win']} predictions")
                    st.error(f"❌ **False Win**: {cm['false_win']} predictions\n(Actually lost)")

                with col2:
                    st.markdown("**Predicted: Loss**")
                    st.info(f"✅ **True Loss**: {cm['true_loss']} predictions")
                    st.error(f"❌ **False Loss**: {cm['false_loss']} predictions\n(Actually won)")

        elif stats and 'error' in stats:
            st.warning(f"⚠️ Unable to calculate accuracy statistics: {stats['error']}")
        else:
            st.info("Unable to calculate accuracy statistics.")
    elif not session_ratings:
        st.info("No ratings found in current session. Accuracy statistics are only shown for videos rated in this session.")
    else:
        st.warning(f"⚠️ Cannot calculate accuracy: Metadata is {'empty' if metadata.empty else 'missing WinLoss column'}")

    st.markdown("---")
    st.markdown("""
    Your responses have been saved and will help us understand emotion decoding in athletes.

    You may now close this window.
    """)

    # Navigation button
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("◀️ Back to Questionnaire", use_container_width=True):
            st.session_state.page = 'questionnaire'
            st.session_state.user_id_confirmed = False
            st.session_state.video_initialized = False
            st.session_state.session_ratings = {}  # Clear session ratings
            st.rerun()
