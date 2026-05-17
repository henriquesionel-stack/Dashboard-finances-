import streamlit as st

import yfinance as yf

import pandas as pd

import plotly.express as px

st.set_page_config(

    page_title="Dashboard Finance Ionel",

    layout="wide",

    page_icon="📊"

)

st.markdown("""

<style>

.main {

    background-color: #0f172a;

}

.block-container {

    padding-top: 2rem;

}

[data-testid="stMetricValue"] {

    font-size: 26px;

}

</style>

""", unsafe_allow_html=True)

st.title("📊 Dashboard Finance Ionel")

st.caption("Screener investisseur multi-actifs · données Yahoo Finance · prototype live")

actions_disponibles = {

    "Apple": "AAPL",

    "Nvidia": "NVDA",

    "ASML": "ASML",

    "LVMH": "MC.PA",

    "Microsoft": "MSFT",

    "Tesla": "TSLA",

    "Hermès": "RMS.PA",

    "L'Oréal": "OR.PA"

}

with st.sidebar:

    st.header("⚙️ Paramètres")

    selection = st.multiselect(

        "Actions à suivre",

        list(actions_disponibles.keys()),

        default=["Apple", "Nvidia", "ASML", "LVMH"]

    )

    periode = st.selectbox(

        "Période d’analyse",

        ["1mo", "3mo", "6mo", "1y"],

        index=0

    )

    bouton_refresh = st.button("🔄 Rafraîchir les données")

@st.cache_data(ttl=3600)

def recuperer_donnees(selection, periode):

    resultats = []

    courbes = []

    for nom in selection:

        ticker = actions_disponibles[nom]

        action = yf.Ticker(ticker)

        data = action.history(period=periode)

        info = action.info

        if data.empty:

            continue

        prix = round(data["Close"].iloc[-1], 2)

        performance = round(

            (data["Close"].iloc[-1] / data["Close"].iloc[0] - 1) * 100,

            2

        )

        market_cap = info.get("marketCap")

        per = info.get("trailingPE")

        marge_nette = info.get("profitMargins")

        marge_ope = info.get("operatingMargins")

        roe = info.get("returnOnEquity")

        dette = info.get("totalDebt")

        cash = info.get("totalCash")

        fcf = info.get("freeCashflow")

        secteur = info.get("sector")

        resultats.append({

            "Entreprise": nom,

            "Ticker": ticker,

            "Secteur": secteur,

            "Prix": prix,

            "Performance (%)": performance,

            "Cap. boursière (Md$)": round(market_cap / 1_000_000_000, 2) if market_cap else None,

            "PER": round(per, 2) if per else None,

            "Marge nette (%)": round(marge_nette * 100, 2) if marge_nette else None,

            "Marge opé (%)": round(marge_ope * 100, 2) if marge_ope else None,

            "ROE (%)": round(roe * 100, 2) if roe else None,

            "Dette (Md$)": round(dette / 1_000_000_000, 2) if dette else None,

            "Cash (Md$)": round(cash / 1_000_000_000, 2) if cash else None,

            "FCF (Md$)": round(fcf / 1_000_000_000, 2) if fcf else None

        })

        data = data.reset_index()

        data["Date"] = pd.to_datetime(data["Date"]).dt.tz_localize(None)

        data["Performance base 100"] = (data["Close"] / data["Close"].iloc[0]) * 100

        data["Entreprise"] = nom

        courbes.append(data[["Date", "Entreprise", "Performance base 100"]])

    return pd.DataFrame(resultats), pd.concat(courbes) if courbes else pd.DataFrame()

if bouton_refresh:

    st.cache_data.clear()

tableau, graph_data = recuperer_donnees(selection, periode)

if tableau.empty:

    st.warning("Aucune donnée disponible.")

    st.stop()

tableau = tableau.sort_values(

    by="Performance (%)",

    ascending=False

).reset_index(drop=True)

leader_perf = tableau.iloc[0]

leader_cap = tableau.sort_values(by="Cap. boursière (Md$)", ascending=False).iloc[0]

leader_marge = tableau.sort_values(by="Marge nette (%)", ascending=False).iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric(

    "🏆 Meilleure performance",

    leader_perf["Entreprise"],

    f"{leader_perf['Performance (%)']} %"

)

col2.metric(

    "💰 Plus grosse capitalisation",

    leader_cap["Entreprise"],

    f"{leader_cap['Cap. boursière (Md$)']:.0f} Md$"

)

col3.metric(

    "📈 Meilleure marge nette",

    leader_marge["Entreprise"],

    f"{leader_marge['Marge nette (%)']:.2f} %"

)

tab1, tab2, tab3 = st.tabs([

    "📊 Performance",

    "🏦 Fondamentaux",

    "🧠 Synthèse"

])

with tab1:

    st.subheader("Performance relative — Base 100")

    fig = px.line(

        graph_data,

        x="Date",

        y="Performance base 100",

        color="Entreprise",

        markers=True,

        title=f"Performance relative sur {periode}"

    )

    fig.update_layout(

        template="plotly_dark",

        height=600,

        hovermode="x unified"

    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:

    st.subheader("Tableau fondamental")

    st.dataframe(

        tableau,

        use_container_width=True

    )

    st.subheader("Capitalisations boursières")

    fig_cap = px.bar(

        tableau.sort_values(by="Cap. boursière (Md$)", ascending=False),

        x="Entreprise",

        y="Cap. boursière (Md$)",

        title="Comparaison des capitalisations boursières"

    )

    fig_cap.update_layout(

        template="plotly_dark",

        height=450

    )

    st.plotly_chart(fig_cap, use_container_width=True)

with tab3:

    st.subheader("Synthèse automatique")

    st.success(

        f"{leader_perf['Entreprise']} affiche la meilleure dynamique boursière du panier "

        f"avec une performance de {leader_perf['Performance (%)']} % sur la période."

    )

    st.info(

        f"{leader_cap['Entreprise']} domine le panier en taille de marché "

        f"avec une capitalisation d’environ {leader_cap['Cap. boursière (Md$)']:.0f} Md$."

    )

    st.warning(

        "Cette analyse reste un prototype. La prochaine étape sera d’ajouter un vrai score "

        "d’attractivité intégrant ROIC, dette nette, croissance, valorisation, moat et newsflow."

    )
