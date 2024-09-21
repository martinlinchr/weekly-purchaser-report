import streamlit as st
import pandas as pd
from scraper import get_data, create_graph, REGIONS

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

# Sidebar for data source selection
st.sidebar.title("Select Data Sources")

# Commodities multiselect
st.sidebar.subheader("Commodities")
selected_commodities = st.sidebar.multiselect("Select commodities", list(data_sources['Commodities'].keys()))

# Economic Indicators multiselect
st.sidebar.subheader("Economic Indicators")
selected_indicators = st.sidebar.multiselect("Select economic indicators", list(data_sources['Economic Indicators'].keys()))

# Inflation data multiselect
st.sidebar.subheader("Inflation Data")
selected_inflations = st.sidebar.multiselect("Select regions for inflation data", list(inflation_urls.keys()))

if st.sidebar.button("Fetch Selected Data"):
    # Fetch commodity data
    for selected_commodity in selected_commodities:
        st.subheader(selected_commodity)
        with st.spinner(f"Fetching data for {selected_commodity}..."):
            if selected_commodity == 'Trading Economics Commodities':
                commodity, df = get_data(data_sources['Commodities'][selected_commodity])
                if df is not None:
                    st.dataframe(df)
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
                        st.dataframe(df)
                        
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label=f"Download {selected_commodity} data as CSV",
                            data=csv,
                            file_name=f"{selected_commodity.lower().replace(' ', '_')}_data.csv",
                            mime="text/csv",
                        )
                else:
                    st.error(f"No data found for {selected_commodity}. Please try again.")

    # Fetch economic indicator data
    for selected_indicator in selected_indicators:
        st.subheader(selected_indicator)
        with st.spinner(f"Fetching data for {selected_indicator}..."):
            indicator, details, df, _, _ = get_data(data_sources['Economic Indicators'][selected_indicator], is_ranking=True)
            if indicator and details:
                st.success(f"Data fetched successfully for {selected_indicator}!")
                for key, value in details.items():
                    st.write(f"{key.capitalize()}: {value}")
                if df is not None and not df.empty:
                    st.subheader("Data Table")
                    st.dataframe(df)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label=f"Download {selected_indicator} data as CSV",
                        data=csv,
                        file_name=f"{selected_indicator.lower().replace(' ', '_')}_data.csv",
                        mime="text/csv",
                    )
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
                for key, value in details.items():
                    st.write(f"{key.capitalize()}: {value}")
                if df is not None and not df.empty:
                    st.subheader("Data Table")
                    st.dataframe(df)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label=f"Download inflation data for {selected_inflation} as CSV",
                        data=csv,
                        file_name=f"inflation_{selected_inflation.lower().replace(' ', '_')}_data.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("No data available.")
            else:
                st.error(f"No inflation data found for {selected_inflation}. Please try again.")

# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.info("Select the data sources you want to analyze, then click 'Fetch Selected Data'.")
