import streamlit as st
import pandas as pd
from scraper import get_data, create_graph, REGIONS
from openai import OpenAI
import json
from fpdf import FPDF
import base64
import plotly

# Debug: Print a masked version of the API key
api_key = st.secrets["OPENAI_API_KEY"]
st.write(f"API Key (first 5 chars): {api_key[:5]}...")
st.write(f"API Key length: {len(api_key)}")

# Initialize the OpenAI client with the API key from Streamlit secrets
client = OpenAI(api_key=api_key)

st.title("Economic Data Analyzer")

# Data source selection
data_sources = {
    'Commodities': {
        'Trading Economics Commodities': 'https://tradingeconomics.com/commodities',
        'Brent Oil Prices': 'https://www.theglobaleconomy.com/world/brent_oil_prices/',
        'Gold Prices': 'https://www.theglobaleconomy.com/world/gold_prices/',
        'Silver Prices': 'https://www.theglobaleconomy.com/world/silver_prices/',
        'Aluminum Prices': 'https://www.theglobaleconomy.com/world/aluminum_prices/',
        'Copper Prices': 'https://www.theglobaleconomy.com/world/copper_prices/',
        'Natural Gas Europe': 'https://www.theglobaleconomy.com/world/natural_gas_europe/',
        'Natural Gas USA': 'https://www.theglobaleconomy.com/world/natural_gas_usa/',
        'Dubai Oil Prices': 'https://www.theglobaleconomy.com/world/dubai_oil_prices/',
        'WTI Oil Prices': 'https://www.theglobaleconomy.com/world/wti_oil_prices/',
    },
    'Economic Indicators': {
        'PMI Services': 'https://www.theglobaleconomy.com/rankings/pmi_services/',
        'PMI Composite': 'https://www.theglobaleconomy.com/rankings/pmi_composite/',
        'PMI Manufacturing': 'https://www.theglobaleconomy.com/rankings/pmi_manufacturing/',
        'Unemployment Rate': 'https://www.theglobaleconomy.com/rankings/Unemployment_rate/',
        'Government Debt': 'https://www.theglobaleconomy.com/rankings/Government_debt/',
        'GDP Growth Outlook (IMF)': 'https://www.theglobaleconomy.com/rankings/gdp_growth_outlook_imf/',
        'Inflation Outlook (IMF)': 'https://www.theglobaleconomy.com/rankings/inflation_outlook_imf/',
        'Unemployment Outlook': 'https://www.theglobaleconomy.com/rankings/unemployment_outlook/',
        'Gasoline Prices': 'https://www.theglobaleconomy.com/rankings/gasoline_prices/',
        'Diesel Prices': 'https://www.theglobaleconomy.com/rankings/diesel_prices/',
    }
}

inflation_urls = {
    'Europe': 'https://www.theglobaleconomy.com/rankings/Inflation/Europe/',
    'European Union': 'https://www.theglobaleconomy.com/rankings/Inflation/European-union/',
    'Eurozone': 'https://www.theglobaleconomy.com/rankings/Inflation/Eurozone/',
    'Asia': 'https://www.theglobaleconomy.com/rankings/Inflation/Asia/',
    'Australia': 'https://www.theglobaleconomy.com/rankings/Inflation/Australia/',
    'South America': 'https://www.theglobaleconomy.com/rankings/Inflation/South-America/',
    'North America': 'https://www.theglobaleconomy.com/rankings/Inflation/North-America/',
    'Africa': 'https://www.theglobaleconomy.com/rankings/Inflation/Africa/',
    'MENA': 'https://www.theglobaleconomy.com/rankings/Inflation/MENA/',
    'G7': 'https://www.theglobaleconomy.com/rankings/Inflation/G7/',
    'G20': 'https://www.theglobaleconomy.com/rankings/Inflation/G20/',
    'OPEC': 'https://www.theglobaleconomy.com/rankings/Inflation/OPEC/',
    'NATO': 'https://www.theglobaleconomy.com/rankings/Inflation/NATO/',
    'MSCI Emerging Markets': 'https://www.theglobaleconomy.com/rankings/Inflation/MSCI-Emerging-Markets/',
    'MSCI Frontier Markets': 'https://www.theglobaleconomy.com/rankings/Inflation/MSCI-Frontier-Markets/',
    'MSCI Developed Markets': 'https://www.theglobaleconomy.com/rankings/Inflation/MSCI-Developed%20Markets/'
}

# Function to create a download link for a given file
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{bin_file}">{file_label}</a>'
    return href

# Function to create PDF of fetched data
def create_fetched_data_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for key, df in st.session_state.all_data.items():
        pdf.cell(200, 10, txt=f"{key}:", ln=True, align='L')
        pdf.ln(5)
        
        # Convert dataframe to list of lists for easier iteration
        data = [df.columns.tolist()] + df.values.tolist()
        
        # Determine column widths
        col_widths = [max(len(str(item)) for item in col) * 2 for col in zip(*data)]
        
        for row in data:
            for i, item in enumerate(row):
                pdf.cell(col_widths[i], 10, str(item), border=1)
            pdf.ln()
        
        pdf.ln(10)
        
        if key in st.session_state.fetched_data_details:
            details = st.session_state.fetched_data_details[key]
            if 'details' in details:
                for detail_key, detail_value in details['details'].items():
                    pdf.cell(200, 10, txt=f"{detail_key.capitalize()}: {detail_value}", ln=True, align='L')
            pdf.ln(5)
    
    pdf.output("fetched_data.pdf")

# Function to create PDF of AI chat
def create_ai_chat_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="AI Chat History", ln=True, align='C')
    pdf.ln(10)
    
    for role, message in st.session_state.chat_history:
        pdf.multi_cell(0, 10, txt=f"{role}: {message}", align='L')
        pdf.ln(5)
    
    pdf.output("ai_chat.pdf")

# Function to reset the app
def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

# Sidebar for data source selection
st.sidebar.title("Select Data Sources")
st.sidebar.info("Select the data sources you want to analyze, then click 'Fetch Selected Data'.")

# Commodities multiselect
st.sidebar.subheader("Commodities")
selected_commodities = st.sidebar.multiselect("Select commodities", list(data_sources['Commodities'].keys()))

# Economic Indicators multiselect
st.sidebar.subheader("Economic Indicators")
selected_indicators = st.sidebar.multiselect("Select economic indicators", list(data_sources['Economic Indicators'].keys()))

# Inflation data multiselect
st.sidebar.subheader("Inflation Data")
selected_inflations = st.sidebar.multiselect("Select regions for inflation data", list(inflation_urls.keys()))

# Reset button
if st.sidebar.button("Reset App"):
    reset_app()

# Function to chat with AI about the data
def chat_with_ai(data_description, user_question):
    try:
        prompt = f"Based on the following economic data:\n\n{data_description}\n\nUser question: {user_question}\n\nAnswer:"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant that analyzes economic data and answers questions about it."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"An error occurred while communicating with the AI: {str(e)}")
        return None

# Initialize session state
if 'all_data' not in st.session_state:
    st.session_state.all_data = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'fetched_data_details' not in st.session_state:
    st.session_state.fetched_data_details = {}

if st.sidebar.button("Fetch Selected Data"):
    st.session_state.all_data = {}  # Reset all_data
    st.session_state.fetched_data_details = {}  # Reset fetched_data_details

    # Fetch commodity data
    for selected_commodity in selected_commodities:
        st.subheader(selected_commodity)
        with st.spinner(f"Fetching data for {selected_commodity}..."):
            if selected_commodity == 'Trading Economics Commodities':
                commodity, df = get_data(data_sources['Commodities'][selected_commodity])
                if df is not None:
                    st.dataframe(df.round(2))
                    st.session_state.all_data[selected_commodity] = df
            else:
                commodity, details, df, recent_graph_url, historical_graph_url = get_data(data_sources['Commodities'][selected_commodity])
                if commodity and details:
                    st.success(f"Data fetched successfully for {selected_commodity}!")
                    for key, value in details.items():
                        st.write(f"{key.capitalize()}: {value}")
                    if recent_graph_url:
                        st.subheader("Recent Values")
                        st.image(recent_graph_url, use_column_width=True)
                    if historical_graph_url:
                        st.subheader("Longer Historical Series")
                        st.image(historical_graph_url, use_column_width=True)
                    if df is not None and not df.empty:
                        st.subheader("Data Summary")
                        st.dataframe(df.round(2))
                        st.session_state.all_data[selected_commodity] = df
                        
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label=f"Download {selected_commodity} data as CSV",
                            data=csv,
                            file_name=f"{selected_commodity.lower().replace(' ', '_')}_data.csv",
                            mime="text/csv",
                        )
                    
                    # Store details and graph URLs
                    st.session_state.fetched_data_details[selected_commodity] = {
                        'details': details,
                        'recent_graph_url': recent_graph_url,
                        'historical_graph_url': historical_graph_url
                    }
                else:
                    st.error(f"No data found for {selected_commodity}. Please try again.")

    # Fetch economic indicator data
    for selected_indicator in selected_indicators:
        st.subheader(selected_indicator)
        with st.spinner(f"Fetching data for {selected_indicator}..."):
            indicator, details, df, _, _ = get_data(data_sources['Economic Indicators'][selected_indicator], is_ranking=True)
            if indicator and details:
                st.success(f"Data fetched successfully for {selected_indicator}!")
                if df is not None and not df.empty:
                    st.subheader("Data Table")
                    df = df.round(2)
                    st.dataframe(df)
                    st.session_state.all_data[selected_indicator] = df
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label=f"Download {selected_indicator} data as CSV",
                        data=csv,
                        file_name=f"{selected_indicator.lower().replace(' ', '_')}_data.csv",
                        mime="text/csv",
                    )
                    
                    # Store details
                    st.session_state.fetched_data_details[selected_indicator] = {'details': details}
                else:
                    st.warning("No data available.")
            else:
                st.error(f"No data found for {selected_indicator}. Please try again.")

    # Fetch inflation data
    for selected_inflation in selected_inflations:
        st.subheader(f"Inflation Data for {selected_inflation}")
        with st.spinner(f"Fetching inflation data for {selected_inflation}..."):
            indicator, details, df, _, _ = get_data(inflation_urls[selected_inflation], is_ranking=True)
            if indicator and details:
                st.success(f"Inflation data fetched successfully for {selected_inflation}!")
                if df is not None and not df.empty:
                    st.subheader("Data Table")
                    df = df.round(2)
                    st.dataframe(df)
                    st.session_state.all_data[f"Inflation - {selected_inflation}"] = df
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label=f"Download inflation data for {selected_inflation} as CSV",
                        data=csv,
                        file_name=f"inflation_{selected_inflation.lower().replace(' ', '_')}_data.csv",
                        mime="text/csv",
                    )
                    
                    # Store details
                    st.session_state.fetched_data_details[f"Inflation - {selected_inflation}"] = {'details': details}
                else:
                    st.warning("No data available.")
            else:
                st.error(f"No inflation data found for {selected_inflation}. Please try again.")

# Display fetched data and details
if st.session_state.all_data:
    st.subheader("Fetched Data")
    for key, df in st.session_state.all_data.items():
        st.write(f"{key}:")
        st.dataframe(df.round(2))
        
        if key in st.session_state.fetched_data_details:
            details = st.session_state.fetched_data_details[key]
            if 'details' in details:
                for detail_key, detail_value in details['details'].items():
                    st.write(f"{detail_key.capitalize()}: {detail_value}")
            if 'recent_graph_url' in details and details['recent_graph_url']:
                st.subheader("Recent Values")
                st.image(details['recent_graph_url'], use_column_width=True)
            if 'historical_graph_url' in details and details['historical_graph_url']:
                st.subheader("Longer Historical Series")
                st.image(details['historical_graph_url'], use_column_width=True)

    # Button to create PDF of fetched data
    if st.button("Create PDF of Fetched Data"):
        create_fetched_data_pdf()
        st.markdown(get_binary_file_downloader_html('fetched_data.pdf', 'Download Fetched Data PDF'), unsafe_allow_html=True)

# Chat with AI about the data
if st.session_state.all_data:
    st.subheader("Chat with AI about the Data")
    
    # Select specific data to chat about
    data_to_chat = st.multiselect("Select data to chat about", list(st.session_state.all_data.keys()))
    
    user_question = st.text_input("Ask a question about the selected data:")
    if user_question and data_to_chat:
        data_description = "\n".join([f"{key}:\n{st.session_state.all_data[key].to_string()}\n" for key in data_to_chat])
        with st.spinner("AI is analyzing the data..."):
            ai_response = chat_with_ai(data_description, user_question)
        if ai_response:
            st.session_state.chat_history.insert(0, ("AI", ai_response))
            st.session_state.chat_history.insert(0, ("User", user_question))

    # Display chat history
    st.subheader("Chat History")
    for role, message in st.session_state.chat_history:
        st.write(f"{role}: {message}")

    # Download chat history as JSON
    if st.session_state.chat_history:
        chat_history_str = json.dumps(st.session_state.chat_history, indent=2)
        st.download_button(
            label="Download Chat History as JSON",
            data=chat_history_str,
            file_name="chat_history.json",
            mime="application/json"
        )

    # Button to create PDF of AI chat
    if st.button("Create PDF of AI Chat"):
        create_ai_chat_pdf()
        st.markdown(get_binary_file_downloader_html('ai_chat.pdf', 'Download AI Chat PDF'), unsafe_allow_html=True)

else:
    st.info("Fetch some data first to chat with the AI about it.")

# Run the Streamlit app
if __name__ == "__main__":
    pass
