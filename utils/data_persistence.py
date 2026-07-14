"""
Data persistence functions for saving and loading user data and ratings.
Implements flexible storage strategy based on config: local, online, or both.
"""
import json
import os
import streamlit as st
from datetime import datetime
from utils.gsheets_manager import (
    append_rating_to_gsheets,
    get_rated_videos_for_user_from_gsheets,
    append_user_to_gsheets,
    user_exists_in_gsheets
)

def save_user_data(user):
    user_data = user.to_dict()
    config = st.session_state.get('config', {})
    storage_mode = config.get('settings', {}).get('storage_mode', 'both')

    gsheets_success = False
    local_json_success = False

    if storage_mode in ['online', 'both']:
        try:
            gsheets_success = append_user_to_gsheets(user_data, worksheet="Demographics")
            if gsheets_success:
                print(f"[INFO] ✓ User data saved to Google Sheets: {user.user_id}")
        except Exception as e:
            print(f"[WARNING] Google Sheets write failed for user data: {e}")

    if storage_mode in ['local', 'both']:
        try:
            os.makedirs('user_data', exist_ok=True)
            filename = f"{user.user_id}.json"
            path = os.path.join('user_data', filename)

            with open(path, 'w') as f:
                json.dump(user_data, f, indent=2)

            local_json_success = True
            print(f"[INFO] ✓ User data saved to local JSON: {filename}")
        except Exception as e:
            print(f"[WARNING] Local JSON write failed for user data: {e}")

    success = gsheets_success or local_json_success
    if success:
        return True
    else:
        print(f"[ERROR] CRITICAL: All storage methods failed for user {user.user_id}")
        return False

def save_rating(user_id, action_id, scale_values):
    rating_data = {
        'user_id': user_id,
        'id': action_id
    }

    for title, value in scale_values.items():
        key = title.lower().replace(' ', '_')
        rating_data[key] = value

    device_info = st.session_state.get('device_info', {})
    if device_info:
        rating_data['device_type'] = device_info.get('device_type')
        rating_data['os'] = device_info.get('os')
        rating_data['browser'] = device_info.get('browser')
        rating_data['browser_version'] = device_info.get('browser_version')
        rating_data['maxTouchPoints'] = device_info.get('maxTouchPoints')
        rating_data['screen_width'] = device_info.get('screen_width')
        rating_data['screen_height'] = device_info.get('screen_height')
        rating_data['user_agent'] = device_info.get('user_agent')

    config = st.session_state.get('config', {})
    storage_mode = config.get('settings', {}).get('storage_mode', 'both')

    gsheets_success = False
    local_json_success = False

    if storage_mode in ['online', 'both']:
        try:
            gsheets_success = append_rating_to_gsheets(rating_data, worksheet="Ratings")
            if gsheets_success:
                print(f"[INFO] ✓ Rating saved to Google Sheets: {user_id}_{action_id}")
        except Exception as e:
            print(f"[WARNING] Google Sheets write failed: {e}")

    if storage_mode in ['local', 'both']:
        try:
            os.makedirs('user_ratings', exist_ok=True)
            filename = os.path.join('user_ratings', f"{user_id}_{action_id}.json")
            with open(filename, 'w') as f:
                json.dump(rating_data, f, indent=2)
            local_json_success = True
            print(f"[INFO] ✓ Rating saved to local JSON: {user_id}_{action_id}.json")
        except Exception as e:
            print(f"[WARNING] Local JSON write failed: {e}")

    success = gsheets_success or local_json_success
    if success:
        return True
    else:
        print(f"[ERROR] CRITICAL: All storage methods failed for {user_id}_{action_id}")
        return False

def get_all_existing_user_ids():
    user_ids = set()

    try:
        from utils.gsheets_manager import get_all_user_ids_from_gsheets
        gsheets_ids = get_all_user_ids_from_gsheets(worksheet="Demographics")
        user_ids.update(gsheets_ids)
        print(f"[INFO] Retrieved {len(gsheets_ids)} user IDs from Google Sheets")
    except Exception as e:
        print(f"[WARNING] Failed to get user IDs from Google Sheets: {e}")

    try:
        if os.path.exists('user_data'):
            for filename in os.listdir('user_data'):
                if filename.endswith('.json'):
                    user_id = filename.replace('.json', '')
                    user_ids.add(user_id)
            print(f"[INFO] Found {len(user_ids)} total unique user IDs")
    except Exception as e:
        print(f"[WARNING] Failed to get user IDs from local files: {e}")

    return list(user_ids)

def user_exists(user_id):
    try:
        if user_exists_in_gsheets(user_id, worksheet="Demographics"):
            print(f"[INFO] User {user_id} found in Google Sheets")
            return True
    except Exception as e:
        print(f"[WARNING] Failed to check user existence in Google Sheets: {e}")

    try:
        if not os.path.exists('user_data'):
            return False

        user_id_lower = user_id.lower()
        for filename in os.listdir('user_data'):
            if filename.endswith('.json'):
                file_user_id = filename.replace('.json', '').lower()
                if file_user_id == user_id_lower:
                    print(f"[INFO] User {user_id} found in local JSON files")
                    return True

        if not os.path.exists('user_ratings'):
            return False

        user_ratings_files = os.listdir('user_ratings')
        for f in user_ratings_files:
            if '_' in f and f.endswith('.json'):
                file_user_id = f.split('_')[0].lower()
                if file_user_id == user_id_lower:
                    print(f"[INFO] User {user_id} found in local JSON files")
                    return True

        return False
    except Exception as e:
        print(f"[ERROR] Failed to check user existence in both sources: {e}")
        return False

def get_rated_videos_for_user(user_id):
    try:
        gsheets_ids = get_rated_videos_for_user_from_gsheets(user_id, worksheet="Ratings")
        if gsheets_ids:
            print(f"[INFO] Retrieved {len(gsheets_ids)} rated videos from Google Sheets for user {user_id}")
            return gsheets_ids
    except Exception as e:
        print(f"[WARNING] Failed to get rated videos from Google Sheets: {e}")

    try:
        if not os.path.exists('user_ratings'):
            return []

        files = os.listdir('user_ratings')
        rated_ids = []
        user_id_lower = user_id.lower()

        for f in files:
            if f.endswith('.json') and '_' in f:
                file_user_id = f.split('_')[0].lower()
                if file_user_id == user_id_lower:
                    parts = f.replace('.json', '').split('_', 1)
                    if len(parts) > 1:
                        action_id = parts[1]
                        rated_ids.append(action_id)

        print(f"[INFO] Retrieved {len(rated_ids)} rated videos from JSON backup for user {user_id}")
        return rated_ids
    except Exception as e:
        print(f"[ERROR] Failed to get rated videos from both sources: {e}")
        return []
