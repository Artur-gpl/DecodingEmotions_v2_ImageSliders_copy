"""
Google Sheets manager for data persistence.
Handles connections and write operations to Google Sheets.
"""
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Global connection cache
_gsheets_connection = None
_gspread_client = None

USERS_WORKSHEET = "users_noface"
RATINGS_WORKSHEET = "ratings_noface"


def get_gsheets_connection():
    """
    Get or create a cached Google Sheets connection.

    Returns:
        GSheetsConnection object or None if connection fails
    """
    global _gsheets_connection

    if _gsheets_connection is None:
        try:
            _gsheets_connection = st.connection("gsheets", type=GSheetsConnection)
            print("[INFO] Google Sheets connection established")
        except Exception as e:
            print(f"[ERROR] Failed to create Google Sheets connection: {e}")
            return None

    return _gsheets_connection


def get_gspread_client():
    """
    Get or create a cached gspread client directly from secrets.
    This is used for advanced operations like append_row.

    Returns:
        gspread.Client object or None if connection fails
    """
    global _gspread_client

    if _gspread_client is None:
        try:
            credentials_dict = dict(st.secrets["connections"]["gsheets"])
            credentials_dict.pop("spreadsheet", None)

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]

            credentials = Credentials.from_service_account_info(
                credentials_dict,
                scopes=scopes
            )

            _gspread_client = gspread.authorize(credentials)
            print("[INFO] gspread client created successfully")

        except Exception as e:
            print(f"[ERROR] Failed to create gspread client: {e}")
            import traceback
            traceback.print_exc()
            return None

    return _gspread_client


def append_rating_to_gsheets(rating_data, worksheet=RATINGS_WORKSHEET):
    """
    Append a single rating row to Google Sheets using true append (no overwrite).
    """
    try:
        gspread_client = get_gspread_client()
        if gspread_client is None:
            print("[WARNING] No gspread client available")
            return False

        rating_data_with_timestamp = rating_data.copy()
        rating_data_with_timestamp['timestamp'] = datetime.now().isoformat()

        spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        spreadsheet = gspread_client.open_by_url(spreadsheet_url)

        try:
            ws = spreadsheet.worksheet(worksheet)
        except Exception:
            ws = spreadsheet.add_worksheet(title=worksheet, rows=1000, cols=26)
            print(f"[INFO] Created new worksheet: {worksheet}")

        existing_data = ws.get_all_values()

        if len(existing_data) == 0 or (len(existing_data) == 1 and not existing_data[0]):
            headers = list(rating_data_with_timestamp.keys())
            values = list(rating_data_with_timestamp.values())

            ws.append_row(headers, value_input_option='RAW')
            ws.append_row(values, value_input_option='USER_ENTERED')
            print(f"[INFO] Created headers and appended first rating to worksheet: {worksheet}")
        else:
            existing_headers = existing_data[0]
            new_keys = set(rating_data_with_timestamp.keys())
            existing_keys = set(existing_headers)

            if new_keys != existing_keys:
                all_columns = existing_headers + [k for k in new_keys if k not in existing_keys]
                ws.update('1:1', [all_columns], value_input_option='RAW')
                row_values = [rating_data_with_timestamp.get(col, '') for col in all_columns]
            else:
                row_values = [rating_data_with_timestamp.get(col, '') for col in existing_headers]

            ws.append_row(row_values, value_input_option='USER_ENTERED')
            print(f"[INFO] Rating appended to Google Sheets (worksheet: {worksheet})")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to append rating to Google Sheets: {e}")
        import traceback
        traceback.print_exc()
        return False


def read_ratings_from_gsheets(worksheet=RATINGS_WORKSHEET):
    """
    Read all ratings from Google Sheets.
    """
    try:
        conn = get_gsheets_connection()
        if conn is None:
            return pd.DataFrame()

        df = conn.read(worksheet=worksheet, ttl=0)
        print(f"[INFO] Read {len(df)} ratings from Google Sheets")
        return df

    except Exception as e:
        print(f"[ERROR] Failed to read ratings from Google Sheets: {e}")
        return pd.DataFrame()


def get_rated_videos_for_user_from_gsheets(user_id, worksheet=RATINGS_WORKSHEET):
    """
    Get list of video IDs already rated by a specific user from Google Sheets.
    """
    try:
        df = read_ratings_from_gsheets(worksheet=worksheet)

        if df.empty or 'user_id' not in df.columns or 'id' not in df.columns:
            return []

        user_id_lower = user_id.lower()
        df['user_id_lower'] = df['user_id'].astype(str).str.lower()
        user_ratings = df[df['user_id_lower'] == user_id_lower]

        rated_ids = user_ratings['id'].unique().tolist()
        return rated_ids

    except Exception as e:
        print(f"[ERROR] Failed to get rated videos from Google Sheets: {e}")
        return []


def append_user_to_gsheets(user_data, worksheet=USERS_WORKSHEET):
    """
    Append a single user row to Google Sheets using true append (no overwrite).
    """
    try:
        gspread_client = get_gspread_client()
        if gspread_client is None:
            print("[WARNING] No gspread client available")
            return False

        user_data_with_timestamp = user_data.copy()
        user_data_with_timestamp['timestamp'] = datetime.now().isoformat()

        spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        spreadsheet = gspread_client.open_by_url(spreadsheet_url)

        try:
            ws = spreadsheet.worksheet(worksheet)
        except Exception:
            ws = spreadsheet.add_worksheet(title=worksheet, rows=1000, cols=26)
            print(f"[INFO] Created new worksheet: {worksheet}")

        existing_data = ws.get_all_values()

        if len(existing_data) == 0 or (len(existing_data) == 1 and not existing_data[0]):
            headers = list(user_data_with_timestamp.keys())
            values = list(user_data_with_timestamp.values())

            ws.append_row(headers, value_input_option='RAW')
            ws.append_row(values, value_input_option='USER_ENTERED')
            print(f"[INFO] Created headers and appended first user to worksheet: {worksheet}")
        else:
            existing_headers = existing_data[0]
            new_keys = set(user_data_with_timestamp.keys())
            existing_keys = set(existing_headers)

            if new_keys != existing_keys:
                all_columns = existing_headers + [k for k in new_keys if k not in existing_keys]
                ws.update('1:1', [all_columns], value_input_option='RAW')
                row_values = [user_data_with_timestamp.get(col, '') for col in all_columns]
            else:
                row_values = [user_data_with_timestamp.get(col, '') for col in existing_headers]

            ws.append_row(row_values, value_input_option='USER_ENTERED')
            print(f"[INFO] User data appended to Google Sheets (worksheet: {worksheet})")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to append user to Google Sheets: {e}")
        import traceback
        traceback.print_exc()
        return False


def read_users_from_gsheets(worksheet=USERS_WORKSHEET):
    """
    Read all users from Google Sheets.
    """
    try:
        conn = get_gsheets_connection()
        if conn is None:
            return pd.DataFrame()

        df = conn.read(worksheet=worksheet, ttl=0)
        print(f"[INFO] Read {len(df)} users from Google Sheets")
        return df

    except Exception as e:
        print(f"[ERROR] Failed to read users from Google Sheets: {e}")
        return pd.DataFrame()


def user_exists_in_gsheets(user_id, worksheet=USERS_WORKSHEET):
    """
    Check if a user exists in Google Sheets (case-insensitive).
    """
    try:
        df = read_users_from_gsheets(worksheet=worksheet)

        if df.empty or 'user_id' not in df.columns:
            return False

        user_id_lower = user_id.lower()
        df['user_id_lower'] = df['user_id'].astype(str).str.lower()
        return user_id_lower in df['user_id_lower'].values

    except Exception as e:
        print(f"[ERROR] Failed to check user existence in Google Sheets: {e}")
        return False


def get_all_user_ids_from_gsheets(worksheet=USERS_WORKSHEET):
    """
    Get all user IDs from Google Sheets.
    """
    try:
        df = read_users_from_gsheets(worksheet=worksheet)

        if df.empty or 'user_id' not in df.columns:
            return []

        return df['user_id'].dropna().unique().tolist()

    except Exception as e:
        print(f"[ERROR] Failed to get all user IDs from Google Sheets: {e}")
        return []
