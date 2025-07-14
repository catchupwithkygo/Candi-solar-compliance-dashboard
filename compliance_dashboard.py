import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from datetime import datetime
from PIL import Image
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="Candi Solar Compliance Dashboard",
    layout="centered",
    initial_sidebar_state="auto"
    # layout="widece",  # Uncomment if you want a wide layout
    # initial_sidebar_state="expanded"
)

# --- Embedded CSV Data (simulating file input) ---
csv_data = """Client Name,Date of initial contract signing,Date of final credit assessment completed,Subsidiary or a standalone,External credit check
AR - Eagle Heights,02.08.2024,19.06.2024,Subsidiary,Yes
AR - La Hoff,30.06.2024,19.06.2024,Subsidiary,Yes
AR - Lebowa P1 - Kaya Lane,30.06.2024,19.06.2024,Subsidiary,Yes
AR - Sandy Lane,31.07.2024,19.06.2024,Subsidiary,Yes
Bracken Timbers,31.03.2021,Credit assessment data is not detailed on Salesforce,Standalone,Cannot locate credit check information on the Google Drive
Brick & Lintel,12.07.2024,04.07.2024,Subsidiary,Yes
Brick & Lintel P2,24.07.2024,04.07.2024,Subsidiary,Yes
BT Industrial,29.03.2024,14.03.2024,Standalone,Yes
Cascades Lifestyle Centre,09.07.2024,Credit assessment data is not detailed on Salesforce,Standalone,Cannot locate credit check information on the Google Drive
DB - Bongani Pompstasie,01.12.2021,27.09.2021,Subsidiary,Yes
DB - Dammetjie Booster,01.12.2021,27.09.2021,Subsidiary,Yes
DB - Dorp Pompstasies,01.12.2021,27.09.2021,Subsidiary,Yes
DB - Groot Booster,01.12.2021,27.09.2021,Subsidiary,Yes
DB - Stoor Pompstasie,01.12.2021,27.09.2021,Subsidiary,Yes
DB - Torque Booster,01.12.2021,27.09.2021,Subsidiary,Yes
DB - Torque Pompstasie,01.12.2021,27.09.2021,Subsidiary,Yes
Genade P2 1725 Sandrift,01.02.2022,09.02.2023,Subsidiary,Yes
Genade P2 7284 De Bad Booster,01.02.2022,09.02.2023,Subsidiary,Yes
Genade P2 9883 Eureka River,01.02.2022,09.02.2023,Subsidiary,Yes
Genade 1,31.03.2021,09.02.2024,Subsidiary,Yes
Genade P2 - Boskamp,01.06.2023,09.02.2023,Subsidiary,Yes
Genade P2 - Eureka Booster,3.10.2023,09.02.2023,Subsidiary,Yes
Genade P2 - Sandrift Booster 8828,13.10.2023,09.02.2023,Subsidiary,Yes
Genade P3 - De Kalk Dam 7474,28.02.2023,09.02.2023,Subsidiary,Yes
Genade P3 - Olierivier Groot stoor 9753,28.02.2023,09.02.2023,Subsidiary,Yes
Genade P3 - Olierivier Pomp,09.06.2023,09.02.2023,Subsidiary,Yes
Genade P3 - Taaibosrivier 5213,28.02.2023,09.02.2023,Subsidiary,Yes
Givaudan,30.12.2020,Credit assessment data is not detailed on Salesforce,Standalone,Cannot locate credit check information on the Google Drive
HTI Durban,18.08.2020,22.07.2020,Subsidiary,Yes
HTI JHB,07.10.2020,22.07.2020,Subsidiary,Yes
IFF,31.12.2021,07.07.2021,Standalone,Cannot locate credit check information on the Google Drive
Industrial City,31.07.2023,09.02.2023,Standalone,Cannot locate credit check information on the Google Drive
Intaba Building,13.12.2023,Credit assessment not finalised (Prelim stage),Standalone,Cannot locate credit check information on the Google Drive
Java Printing,18.10.2022,13.10.2022,Standalone,Yes
JMS 1 Mthubatba PV,31.12.2021,18.01.2022,Subsidiary,Yes
JMS Hluhluwe,12.07.2024,18.01.2022,Subsidiary,Yes
JMS Hluhluwe BESS only,29.04.2023,18.01.2022,Subsidiary,Yes
JMS Mbazwana,29.02.2024,18.01.2022,Subsidiary,Yes
JMS Mbazwane BESS only,27.10.2023,18.01.2022,Subsidiary,Yes
JMS Mthubatuba BESS only,28.04.2023,18.01.2022,Subsidiary,Yes
La Cote d'Azur,15.12.2022,28.02.2022,Standalone,Cannot locate credit check information on the Google Drive
Lyralinx,14.08.2023,15.02.2023,Standalone,Cannot locate credit check information on the Google Drive
Mooikloof Office Park,13.09.2023,27.07.2023,Standalone,Cannot locate credit check information on the Google Drive
PnP Eshowe,31.12.2023,12.12.2023,Standalone,Cannot locate credit check information on the Google Drive
Reproflex 3,07.11.2022,14.10.2022,Standalone,Cannot locate credit check information on the Google Drive
Reyno Ridge,28.10.2022,Credit assessment yet to be done,Standalone,Cannot locate credit check information on the Google Drive
Riverside,22.10.2020,16.10.2020,Standalone,Yes
Schneider,20.08.2020,21.01.2021,Standalone,Cannot locate credit check information on the Google Drive
Tente,29.03.2021,Credit assessment yet to be done,Standalone,Cannot locate credit check information on the Google Drive
The Sharks - Kings Park,15.09.2023,31.12.2022,Standalone,Yes
Toyota HQ,06.07.2020,29.07.2020,Subsidiary,Cannot locate credit check information on the Google Drive
Toyota HR,21.07.2020,29.07.2020,Subsidiary,Cannot locate credit check information on the Google Drive
Toyota P2,29.07.2020,29.07.2020,Subsidiary,Cannot locate credit check information on the Google Drive
Ngwenya Lodge,29.02.2024,31.12.2022,Standalone,Yes
Tropic Plastics,30.01.2023,28.02.2022,Standalone,Yes"""


# --- Data Loading and Parsing ---
@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(StringIO(csv_data))
    # Try to parse date columns, fallback to NaT if not possible
    for col in ["Date of initial contract signing", "Date of final credit assessment completed"]:
        df[col] = pd.to_datetime(df[col], format="%d.%m.%Y", errors="coerce")
    return df


# --- Enhanced Data Processing for Metrics ---
def process_data(df):
    total_clients = len(df)
    subsidiary_count = (df["Subsidiary or a standalone"] == "Subsidiary").sum()
    standalone_count = total_clients - subsidiary_count

    # Compliance logic
    def is_compliant(row):
        credit_assessment = row["Date of final credit assessment completed"]
        credit_check = row["External credit check"]
        if pd.isna(credit_assessment) or credit_check != "Yes":
            return "Non-Compliant"
        return "Compliant"

    df["Compliance Status"] = df.apply(is_compliant, axis=1)
    compliant_count = (df["Compliance Status"] == "Compliant").sum()
    non_compliant_count = total_clients - compliant_count

    # Additional metrics
    compliance_rate = (compliant_count / total_clients) * \
        100 if total_clients > 0 else 0
    non_compliance_rate = 100 - compliance_rate

    return {
        "total_clients": total_clients,
        "subsidiary_count": subsidiary_count,
        "standalone_count": standalone_count,
        "compliant_count": compliant_count,
        "non_compliant_count": non_compliant_count,
        "compliance_rate": compliance_rate,
        "non_compliance_rate": non_compliance_rate,
        "df": df
    }


# --- Load and Process Data ---
df = load_data()
metrics = process_data(df)

# --- Header with Logo and Title ---
with st.container():
    col1, col2 = st.columns([1, 4])
    with col1:
        # Load logo from local file
        logo_path = "logo.png"  # Make sure logo.png is in the same directory as this script
        try:
            image = Image.open(logo_path)
            st.image(image, width=150)
        except Exception:
            st.write(":sunny:")
        logo_url = "https://www.candi.solar/wp-content/uploads/2022/09/candi-logo.svg"
        try:
            response = requests.get(logo_url, timeout=5)
            if response.status_code == 200:
                image = Image.open(StringIO(response.content))
                st.image(image, width=150)
            else:
                st.write(":sunny:")
        except requests.exceptions.RequestException:
            st.write(":sunny:")
    with col2:
        st.markdown(
            """
            <h1 style='margin-bottom:0;'>Candi Solar Compliance Dashboard</h1>
            <div style='font-size:1.1rem; color:#555;'>Monitor client compliance metrics and trends for Candi Solar.</div>
            """,
            unsafe_allow_html=True
        )


# --- Sidebar for View Selection ---
with st.sidebar:
    st.header(":bar_chart: Dashboard Views")
    view = st.selectbox(
        "Select View",
        ["Summary", "Compliance", "Timeline", "Data Table"],
        index=0
    )


# --- Main Views ---
if view == "Summary":
    st.header(":bar_chart: Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Clients", metrics["total_clients"])
    col2.metric("Subsidiaries", metrics["subsidiary_count"])
    col3.metric("Standalone", metrics["standalone_count"])
    st.info(
        "Most clients are subsidiaries, indicating strong corporate group affiliations.")
    st.markdown("<hr>**Overview**: This dashboard tracks compliance for Candi Solar clients, including credit assessments and external checks.", unsafe_allow_html=True)

elif view == "Compliance":
    st.header(":shield: Compliance Status")
    compliance_counts = metrics["df"]["Compliance Status"].value_counts(
    ).reset_index()
    compliance_counts.columns = ["Status", "Count"]
    fig = px.bar(
        compliance_counts,
        x="Status",
        y="Count",
        color="Status",
        color_discrete_map={"Compliant": "#00CC96",
                            "Non-Compliant": "#EF553B"},
        title="Compliance Status Distribution",
        text="Count"
    )
    fig.update_layout(showlegend=False, title_x=0.5, margin=dict(t=50, b=50))
    st.plotly_chart(fig, use_container_width=True)
    st.warning(
        "Compliant clients have a completed credit assessment and a confirmed external credit check.")

elif view == "Timeline":
    st.header(":date: Contract Signing Timeline")
    valid_dates = metrics["df"].dropna(
        subset=["Date of initial contract signing"])
    if not valid_dates.empty:
        fig = px.scatter(
            valid_dates,
            x="Date of initial contract signing",
            y="Client Name",
            title="Timeline of Contract Signings",
            height=600,
            color_discrete_sequence=["#636EFA"]
        )
        fig.update_traces(marker=dict(size=10))
        fig.update_layout(title_x=0.5, margin=dict(t=50, b=50))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No valid contract signing dates available for the timeline.")

elif view == "Data Table":
    st.header(":clipboard: Client Data Table")
    st.dataframe(
        metrics["df"],
        use_container_width=True,
        column_config={
            "Date of initial contract signing": st.column_config.DateColumn(format="DD.MM.YYYY"),
            "Date of final credit assessment completed": st.column_config.DateColumn(format="DD.MM.YYYY")
        }
    )
    st.caption(
        "Tip: Use the column headers to sort the table, or scroll to view all clients.")
