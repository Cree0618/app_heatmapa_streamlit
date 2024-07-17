import streamlit as st
import pandas as pd
import plotly.graph_objects as go
#import os
import tempfile

def process_file(file, sheet_name, interval_column, consumption_column, title):
    try:
        # Load the data from the selected sheet
        df = pd.read_excel(file, sheet_name=sheet_name)

        # Remove row 0-2
        df = df.drop([0, 1, 2])

        # Set row 1 as header
        df.columns = df.iloc[0]
        df = df.drop([3])

        # Convert the 'Počátek intervalu' column to datetime
        df[interval_column] = pd.to_datetime(df[interval_column], format='%d.%m.%Y %H:%M:%S')

        # Extract the date and time parts for the heatmap
        df['Date'] = df[interval_column].dt.date
        df['Time'] = df[interval_column].dt.time

        df['Consumption'] = df[consumption_column]

        df_cleaned = df.drop_duplicates(subset=['Time', 'Date'])
        pivot_table_cleaned = df_cleaned.pivot(index='Time', columns='Date', values='Consumption')

        # Creating a heatmap using plotly.graph_objects
        heatmap = go.Heatmap(
            z=pivot_table_cleaned.values,
            x=pivot_table_cleaned.columns,
            y=pivot_table_cleaned.index,
            colorscale='Viridis'
        )

        layout = go.Layout(
            title=title,
            xaxis=dict(title='Date'),
            yaxis=dict(title='Time')
        )

        fig = go.Figure(data=[heatmap], layout=layout)

        # Save to a temporary HTML file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            fig.write_html(tmp_file.name)
            tmp_file_path = tmp_file.name

        # Read the HTML file content
        with open(tmp_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        return html_content, tmp_file_path
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, None

# Streamlit app UI
st.title("Generátor heatmapy z PRE excelu")

uploaded_file = st.file_uploader("Vyberte excelový soubor", type=["xlsx"])
if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    sheet_name = st.selectbox("Vyberte Excel Sešit:", sheet_names)
    
    if sheet_name:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        df = df.drop([0, 1, 2])
        df.columns = df.iloc[0]
        df = df.drop([3])
        columns = df.columns.tolist()
        
        interval_column = st.selectbox("Vyberte sloupec 'Počátek intervalu':", columns)
        consumption_column = st.selectbox("Vyberte sloupec 'Celkem Činná - spotřeba[kW]':", columns)
        
        output_file_name = st.text_input("Název souboru:", "heatmap.html")
        title = st.text_input("Název Heatmapy:", "Heatmapa spotřeby elektřiny")

        if st.button("Generovat Heatmapu"):
            html_content, tmp_file_path = process_file(uploaded_file, sheet_name, interval_column, consumption_column, title)
            if html_content:
                st.success("Heatmapa byla úspěšně vygenerována!")
                st.plotly_chart(go.Figure(go.Heatmap(
                    z=pivot_table_cleaned.values,
                    x=pivot_table_cleaned.columns,
                    y=pivot_table_cleaned.index,
                    colorscale='Viridis'
                )))
                st.download_button(label="Stáhnout Heatmapu", data=html_content, file_name=output_file_name, mime='text/html')
