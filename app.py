import streamlit as st
import pandas as pd
from scraper import get_data, create_graph

st.title("Economic Data Analyzer")

# Data source selection
data_sources = ['Brent Oil Prices', 'Gold Prices']
selected_source = st.selectbox("Select data source:", data_sources)

if st.button("Fetch Data"):
    if selected_source:
        with st.spinner("Fetching data..."):
            df = get_data(selected_source)
        
        if df is not None and not df.empty:
            st.success("Data fetched successfully!")
            st.dataframe(df)
            
            fig = create_graph(df)
            if fig:
                st.plotly_chart(fig)
            
            # Provide download link for the data
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f"{selected_source.lower().replace(' ', '_')}_data.csv",
                mime="text/csv",
            )
        else:
            st.error("No data found. Please try again.")
    else:
        st.warning("Please select a data source.")

# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.info("Select a data source to analyze economic data.")
