import streamlit as st
import pandas as pd
from scraper import get_data, create_graph

st.title("Economic Data Analyzer")

# Data source selection
data_sources = ['Inflation', 'Food Inflation', 'Commodities', 'Custom URL']
selected_source = st.selectbox("Select data source:", data_sources)

if selected_source == 'Custom URL':
    custom_url = st.text_input("Enter custom URL:")
    if custom_url:
        selected_source = custom_url

# Country input
country = st.text_input("Enter country or region (optional):")

if st.button("Fetch Data"):
    if selected_source:
        with st.spinner("Fetching data..."):
            df = get_data(selected_source, country)
        
        if df is not None and not df.empty:
            st.success("Data fetched successfully!")
            st.dataframe(df)
            
            if country:
                fig = create_graph(df, country)
                if fig:
                    st.plotly_chart(fig)
            
            # Provide download link for the data
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="economic_data.csv",
                mime="text/csv",
            )
        else:
            st.error("No data found. Please check your input and try again.")
    else:
        st.warning("Please select a data source.")

# AI Chat Interface (placeholder for future implementation)
st.header("Chat with AI about the Data")
st.text("AI chat functionality will be implemented in a future update.")

# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.info("Select a data source and optionally enter a country to analyze economic data.")
