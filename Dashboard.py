import streamlit as st
import pandas as pd
import os

# Define the file path
voter_file_path = "C:\Demo\Python\Kalikadevi_Voter_Database.xlsx"

def load_voter_data(file_path):
    if os.path.exists(file_path):
        try:
            voter_data = pd.read_excel(file_path, sheet_name="Voters")
            st.write("Columns in dataset:", voter_data.columns.tolist())  # Debugging
            return voter_data
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
            return None
    else:
        st.error("❌ Voter database file not found!")
        return None

def generate_turnout_insights(voter_data):
    if voter_data is not None:
        if "Division" not in voter_data.columns or "Voted" not in voter_data.columns:
            st.error("Missing required columns in the dataset!")
            return None
        
        insights = (
            voter_data.groupby("Division")
            .agg(
                Total_Voters=("Voter ID", "count"),
                Voted=("Voted", lambda x: (x.str.lower() == "yes").sum())
            )
            .reset_index()
        )
        insights["Turnout Percentage"] = (insights["Voted"] / insights["Total_Voters"]) * 100
        insights["Turnout Percentage"] = insights["Turnout Percentage"].round(2)
        return insights
    return None

# Streamlit UI
st.title("📊 Voter Turnout Dashboard")
st.write("This dashboard displays real-time voter turnout insights by division.")

# Load and process data
voter_data = load_voter_data(voter_file_path)
turnout_insights = generate_turnout_insights(voter_data)

if turnout_insights is not None and not turnout_insights.empty:
    # Display warning for divisions with turnout below 50%
    low_turnout_divisions = turnout_insights[turnout_insights["Turnout Percentage"] < 50]
    if not low_turnout_divisions.empty:
        st.warning("⚠️ Warning: The following divisions have voter turnout below 50%:")
        low_turnout_names = ', '.join(low_turnout_divisions["Division"].tolist())
        st.markdown(f"<p style='color: maroon; font-weight: bold;'>{low_turnout_names}</p>", unsafe_allow_html=True)
    
    st.dataframe(turnout_insights)

    # Display bar chart
    st.bar_chart(turnout_insights.set_index("Division")["Turnout Percentage"])

    # Auto-refresh instruction
    st.write("🔄 **To see updated results, refresh the page after updating the Excel file.**")
else:
    st.warning("No data available to display.")
