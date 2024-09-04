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
            commodity, details, df, graph_url = get_data(selected_source)
        
        if commodity and details:
            st.success("Data fetched successfully!")
            
            st.subheader(commodity)
            for key, value in details.items():
                st.write(f"{key.capitalize()}: {value}")
            
            if graph_url:
                st.image(graph_url, caption="Recent values", use_column_width=True)
            
            if not df.empty:
                st.subheader("Historical Data")
                st.dataframe(df)
                
                fig = create_graph(df, commodity)
                if fig:
                    st.plotly_chart(fig)
                
                # Provide download link for the data
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download historical data as CSV",
                    data=csv,
                    file_name=f"{selected_source.lower().replace(' ', '_')}_data.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No historical data available.")
        else:
            st.error("No data found. Please try again.")
    else:
        st.warning("Please select a data source.")

# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.info("Select a data source to analyze economic data.")
