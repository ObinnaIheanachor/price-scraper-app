import streamlit as st
import pandas as pd
import plotly.express as px
import io
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# Use st.cache_data for caching data
@st.cache_data
def load_data():
    df = pd.read_csv("your_dataset.csv")
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'] + pd.Timedelta(days=230)
    return df

df = load_data()

# Main Title
st.markdown("<h1 style='text-align: center; color: #1F4E79;'>📈 Model Prediction Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top: -10px; margin-bottom: 30px;'>", unsafe_allow_html=True)

# Sidebar Toggle for Mobile
is_mobile = st.checkbox("📱 Show Sidebar (Mobile View)", value=True)

if is_mobile:
    with st.sidebar:
        st.header("🔍 Filter Options")

        model_filter = st.multiselect(
            "Select Model(s):", 
            options=df["Model"].unique(), 
            default=["Prophet", "Regressor", "Actual"]
        )

        price_category_filter = st.selectbox(
            "Select Price Category:", 
            options=df["Price Category"].unique()
        )

        postcode_filter = st.selectbox(
            "Select Postcode:", 
            options=df["postcode"].unique()
        )
else:
    model_filter = ["Prophet", "Regressor", "Actual"]
    price_category_filter = df["Price Category"].unique()[0]
    postcode_filter = df["postcode"].unique()[0]

# Filtered Data
filtered_df = df[
    (df["Model"].isin(model_filter)) &
    (df["Price Category"] == price_category_filter) &
    (df["postcode"] == postcode_filter)
]

# Latest Metrics
latest_actual = filtered_df[filtered_df["Model"] == "Actual"].sort_values("date").iloc[-1]["Value"]
latest_prophet = filtered_df[filtered_df["Model"] == "Prophet"].sort_values("date").iloc[-1]["Value"]
latest_regressor = filtered_df[filtered_df["Model"] == "Regressor"].sort_values("date").iloc[-1]["Value"]

st.markdown(f"### 🏷️ Latest Price Metrics for <span style='color:#1F4E79;'>{postcode_filter}</span>", unsafe_allow_html=True)
st.markdown("")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Actual Price", value=f"£{latest_actual:.2f}")

with col2:
    st.metric(label="Prophet Forecast", value=f"£{latest_prophet:.2f}")

with col3:
    st.metric(label="Regressor Forecast", value=f"£{latest_regressor:.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# Line Chart
fig = px.line(
    filtered_df, 
    x="date", 
    y="Value", 
    color="Model", 
    title=f"📊 Price Trend - {postcode_filter} | {price_category_filter}",
    labels={"Value": "Price", "date": "Date", "Model": "Model Type"}
)

fig.update_layout(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    xaxis=dict(showgrid=False, linecolor='lightgray'),
    yaxis=dict(showgrid=True, gridcolor='lightgray', zeroline=False),
    font=dict(family="Segoe UI", size=13, color="#333333"),
    title_font=dict(size=18, family="Segoe UI", color="#1F4E79"),
    title_x=0.5,
    legend_title_text='',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
)

st.plotly_chart(fig, use_container_width=True)

# Export Section
st.markdown("### 📤 Export Filtered Data")

col_csv, col_pdf = st.columns(2)

with col_csv:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Download CSV",
        data=csv,
        file_name=f"filtered_data_{postcode_filter}.csv",
        mime='text/csv'
    )

with col_pdf:
    def create_pdf(dataframe):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        table_data = [list(dataframe.columns)] + dataframe.astype(str).values.tolist()
        table = Table(table_data)
        table.setStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ])
        doc.build([table])
        buffer.seek(0)
        return buffer

    pdf_data = create_pdf(filtered_df)
    st.download_button(
        label="📄 Download PDF",
        data=pdf_data,
        file_name=f"filtered_data_{postcode_filter}.pdf",
        mime='application/pdf'
    )

# Filtered Data Table
with st.expander("🔎 View Filtered Data"):
    st.dataframe(filtered_df, use_container_width=True)

# Custom CSS Styling
st.markdown("""
    <style>
        /* Global background */
        .stApp {
            background-color: #F8F9FA;
        }

        /* Sticky app bar */
        h1 {
            position: sticky;
            top: 0;
            z-index: 999;
            background-color: #F8F9FA;
            padding: 0.5rem;
            border-bottom: 1px solid #ddd;
        }

        /* Titles and headers */
        h1, h2, h3, h4 {
            font-family: 'Segoe UI', sans-serif;
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #E9EEF6;
            padding: 2rem 1rem;
            border-right: 1px solid #D3D3D3;
        }

        /* Metric labels */
        div[data-testid="stMetricLabel"] {
            font-size: 16px;
            color: #555;
        }

        div[data-testid="stMetricValue"] {
            font-size: 22px;
            font-weight: bold;
            color: #1F4E79;
        }

        /* Hide sidebar completely on small screens */
        @media screen and (max-width: 768px) {
            [data-testid="stSidebar"] {
                display: none !important;
            }
            .css-1d391kg {
                display: none !important;
            }
        }
    </style>
""", unsafe_allow_html=True)
