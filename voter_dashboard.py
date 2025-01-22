import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets API setup
SHEET_ID = "1JV-7YzPOLaAw7GLUth09qICzLmF0BA2P"  # Replace with your Google Sheet ID
SHEET_NAME = "Voters"  # Adjust if your sheet name is different

# Google Cloud Service Account JSON (Upload your credentials.json)
SERVICE_ACCOUNT_FILE = "credentials.json"

# Authenticate and connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scope)
client = gspread.authorize(creds)

# Load voter data from Google Sheet
def load_voter_data():
    try:
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error loading Google Sheet: {e}")
        return None

# Generate voter turnout insights
def generate_turnout_insights(voter_data):
    if voter_data is not None:
        insights = (
            voter_data.groupby("Division")
            .agg(
                Total_Voters=("Voter ID", "count"),
                Voted=("Voted", lambda x: (x == "Yes").sum())
            )
            .reset_index()
        )
        insights["Turnout Percentage"] = (insights["Voted"] / insights["Total_Voters"]) * 100
        insights["Turnout Percentage"] = insights["Turnout Percentage"].round(2)
        return insights
    return None

# Streamlit UI
st.title("📊 Voter Turnout Dashboard (Google Sheets)")
st.write("This dashboard displays real-time voter turnout insights by division.")

voter_data = load_voter_data()
turnout_insights = generate_turnout_insights(voter_data)

if turnout_insights is not None:
    # Display warning for divisions with turnout below 50%
    low_turnout_divisions = turnout_insights[turnout_insights["Turnout Percentage"] < 50]
    if not low_turnout_divisions.empty:
        st.warning("⚠️ Warning: The following divisions have voter turnout below 50%:")
        low_turnout_names = ', '.join(low_turnout_divisions["Division"].tolist())
        st.markdown(f"<p style='color: maroon; font-weight: bold;'>{low_turnout_names}</p>", unsafe_allow_html=True)

    st.dataframe(turnout_insights)

    # Display bar chart
    st.bar_chart(turnout_insights.set_index("Division")["Turnout Percentage"])

    st.write("🔄 **This dashboard updates automatically when the Google Sheet is updated.**")
else:
    st.warning("No data available to display.")
