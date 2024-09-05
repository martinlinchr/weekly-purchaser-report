import streamlit as st
import pandas as pd
from scraper import get_data, create_graph

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
        'Inflation': 'https://www.theglobaleconomy.com/rankings/Inflation/',
        'Unemployment Rate': 'https://www.theglobaleconomy.com/rankings/Unemployment_rate/',
        'Government Debt': 'https://www.theglobaleconomy.com/rankings/Government_debt/',
        'GDP Growth Outlook (IMF)': 'https://www.theglobaleconomy.com/rankings/gdp_growth_outlook_imf/',
        'Inflation Outlook (IMF)': 'https://www.theglobaleconomy.com/rankings/inflation_outlook_imf/',
        'Unemployment Outlook': 'https://www.theglobaleconomy.com/rankings/unemployment_outlook/',
        'Gasoline Prices': 'https://www.theglobaleconomy.com/rankings/gasoline_prices/',
        'Diesel Prices': 'https://www.theglobaleconomy.com/rankings/diesel_prices/',
    }
}

# Sidebar for data source selection
st.sidebar.title("Select Data Sources")

selected_sources = {}
for category, sources in data_sources.items():
    st.sidebar.subheader(category)
    for source, url in sources.items():
        selected_sources[source] = st.sidebar.checkbox(source)

# Country selection for Economic Indicators
if any(selected_sources[source] for source in data_sources['Economic Indicators']):
    country = st.sidebar.text_input("Enter a country for Economic Indicators:")
else:
    country = None

if st.sidebar.button("Fetch Selected Data"):
    for source, selected in selected_sources.items():
        if selected:
            st.subheader(source)
            with st.spinner(f"Fetching data for {source}..."):
                if source == 'Trading Economics Commodities':
                    commodity, df = get_data(source)
                    if df is not None:
                        st.dataframe(df)
                else:
                    is_ranking = source in data_sources['Economic Indicators']
                    url = data_sources['Commodities'].get(source) or data_sources['Economic Indicators'].get(source)
                    commodity, details, df, recent_graph_url, historical_graph_url = get_data(url, is_ranking, country if is_ranking else None)
                
                    if commodity and details:
                        st.success(f"Data fetched successfully for {source}!")
                        
                        for key, value in details.items():
                            st.write(f"{key.capitalize()}: {value}")
                        
                        if recent_graph_url:
                            st.subheader("Recent Values")
                            st.image(recent_graph_url, use_column_width=True)
                        
                        if historical_graph_url:
                            st.subheader("Longer Historical Series")
                            st.image(historical_graph_url, use_column_width=True)
                        
                        if df is not None and not df.empty:
                            st.subheader("Data Table")
                            st.dataframe(df)
                            
                            if not is_ranking:
                                fig = create_graph(df, commodity)
                                if fig:
                                    st.plotly_chart(fig)
                            
                            # Provide download link for the data
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label=f"Download {source} data as CSV",
                                data=csv,
                                file_name=f"{source.lower().replace(' ', '_')}_data.csv",
                                mime="text/csv",
                            )
                        else:
                            st.warning("No data available.")
                    else:
                        st.error(f"No data found for {source}. Please try again.")

# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.info("Select the data sources you want to analyze, then click 'Fetch Selected Data'.")
