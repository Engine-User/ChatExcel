import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import chardet
import csv
from datetime import datetime
import pytz  # For timezone handling
import time  # Corrected import for sleep

st.set_page_config(layout="wide")
st.title('ChatExcel App')
# Add a text block with information about the app
st.markdown("### Hello there, do you wish to talk to your Excel sheets?")

with st.expander(label="Unlock the full potential of your data with ChatExcel"):
    st.markdown("""
        <span style='color: Green;'>
            A powerful web app that transforms CSV files into interactive conversations<br>
            Gain unparalleled insights by plotting custom charts, sorting data on demand, and exporting your findings to your local device with just one click<br>
            -from Engineer
        </span>
    """, unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file is not None:
    st.write("...File Uploaded Successfully!")
    
    @st.cache_data
    def load_data(file):
        if file.name.endswith('.csv'):
            # Detect the file encoding
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            
            # Reset file pointer
            file.seek(0)
            
            # Try to detect the delimiter
            dialect = csv.Sniffer().sniff(file.read(1024).decode(encoding))
            file.seek(0)
            
            # Read the CSV file with the detected encoding and delimiter
            try:
                return pd.read_csv(file, encoding=encoding, sep=dialect.delimiter)
            except Exception as e:
                st.error(f"Error reading the file: {str(e)}")
                # If automatic detection fails, let the user specify the delimiter
                delimiter = st.text_input("Please specify the delimiter used in the CSV file:", ",")
                file.seek(0)
                return pd.read_csv(file, encoding=encoding, sep=delimiter)
        elif file.name.endswith('.xlsx'):
            try:
                return pd.read_excel(file)
            except Exception as e:
                st.error(f"Error reading the file: {str(e)}")
                return None
            
    df = load_data(uploaded_file)
    
    if df is not None and not df.empty:
        all_filtered_df = df.copy()  # Initialize all_filtered_df here

    st.subheader("Data Preview")
    rows_to_show = st.slider("Select the number of rows to preview", 5, 50, 5)
    st.write(df.head(rows_to_show))

    st.subheader("Data Analysis")
    if st.checkbox("Show Data Analytics Summary"):
        st.write(df.describe())

    st.subheader("Column Details")
    col1, col2 = st.columns(2)
    with col1:
        if st.checkbox("Show Column Names"):
            st.write(df.columns.tolist())
    with col2:
        if st.checkbox("Show Column Types"):
            st.write(df.dtypes)

    st.subheader("Data Filtering")
    columns = df.columns.tolist()
    selected_columns = st.multiselect("Select Columns to filter", columns)
    
    if selected_columns:
        filter_container = st.container()
        all_filtered_df = df.copy()
        for column in selected_columns:
            unique_values = df[column].unique()
            selected_values = filter_container.multiselect(f"Select values for {column}", unique_values)
            if selected_values:
                all_filtered_df = all_filtered_df[all_filtered_df[column].isin(selected_values)]
        
        st.write("Filtered Data:")
        st.write(all_filtered_df)

        if st.checkbox("Download Filtered Data"):
            st.download_button(
                label="Download CSV",
                data=all_filtered_df.to_csv(index=False),
                file_name="filtered_data.csv",
                mime="text/csv"
            )

    st.subheader("Data Visualization")
    viz_type = st.radio("Select Visualization Type", ["Line Chart", "Bar Chart", "Scatter Plot", "Histogram", "Box Plot", "Heatmap"])

    x_column = st.selectbox("Select X column", columns)
    y_column = st.selectbox("Select Y column", columns)

    if viz_type != "Heatmap":
        if st.button("Generate Plot"):
            fig, ax = plt.subplots(figsize=(10, 6))

            if viz_type == "Line Chart":
                sns.lineplot(data=all_filtered_df, x=x_column, y=y_column, ax=ax)
            elif viz_type == "Bar Chart":
                sns.barplot(data=all_filtered_df, x=x_column, y=y_column, ax=ax)
            elif viz_type == "Scatter Plot":
                sns.scatterplot(data=all_filtered_df, x=x_column, y=y_column, ax=ax)
            elif viz_type == "Histogram":
                sns.histplot(data=all_filtered_df, x=x_column, ax=ax)
            elif viz_type == "Box Plot":
                sns.boxplot(data=all_filtered_df, x=x_column, y=y_column, ax=ax)

            plt.xticks(rotation=45)
            st.pyplot(fig)
    else:
        if st.button("Generate Heatmap"):
            numeric_df = all_filtered_df.select_dtypes(include=[np.number])
            fig, ax = plt.subplots(figsize=(12, 10))
            sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)

    st.subheader("Data Grouping: Please ensure correct columns are selected")
    if st.checkbox("Group Data"):
        group_column = st.selectbox("Select column to group by", columns)
        agg_column = st.selectbox("Select column to aggregate", columns)
        agg_function = st.selectbox("Select aggregation function", ["mean", "sum", "count", "min", "max"])
        
        grouped_data = all_filtered_df.groupby(group_column)[agg_column].agg(agg_function).reset_index()
        st.write(grouped_data)
        
        if st.button("Plot Grouped Data"):
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=grouped_data, x=group_column, y=agg_column, ax=ax)
            plt.xticks(rotation=45)
            st.pyplot(fig)

else:
    st.write("Waiting for you to Upload a file")
    st.info("Please upload a CSV or Excel file to get started.")
