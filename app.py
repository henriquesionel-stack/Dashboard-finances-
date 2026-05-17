import streamlit as st

import yfinance as yf

import pandas as pd

import plotly.express as px

import feedparser

from urllib.parse import quote

from html import escape

st.set_page_config(

    page_title="Dashboard Finance Ionel",

    layout="wide",

    page_icon="📊"

)

st.markdown("""

<style>

.news-box {

    background: #0f172a;

    border: 1px solid #334155;

    border-radius: 14px;

    padding: 12px;

    height: 360px;

    overflow-y: auto;

}

.news-title {

    font-size: 16px;

    font-weight: 800;

    color: #f8fafc;

    margin-bottom: 10px;

}

.news-item {

    padding: 8px 0;

    border-bottom: 1px solid #334155;

}

.news-company {

    font-size: 11px;

    color: #38bdf8;

    font-weight: 800;

}

.news-headline {

    font-size: 12px;

    color: #f8fafc;

    font-weight: 600;

    line-height: 1.25;

}

.news-link {

    text-decoration: none;

}

.block-container {

    padding-top: 1.5rem;

}

</style>

""", unsafe_allow_html=True)

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

mots_cles_news = {

    "Apple": "Apple action bourse finance",

    "Nvidia": "Nvidia action bourse intelligence artificielle",

    "ASML": "ASML action bourse semi-conducteurs",

    "LVMH": "LVMH action bourse luxe",

    "Microsoft": "Microsoft action bourse finance",

    "Tesla": "Tesla action bourse résultats",

    "Hermès": "Hermès action bourse luxe",

    "L'Oréal": "L'Oréal action bourse résultats"

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

    nombre_news = st.slider(

        "Nombre total d'articles",

        5,

        30,

        10

    )

    if st.button("🔄 Rafraîchir"):

        st.cache_data.clear()

def couper_titre(titre, longueur=50):

    if len(titre) <= longueur:

        return titre

    return titre[:longueur] + "..."

@st.cache_data(ttl=1800)

def recuperer_news_fr(selection, nombre_news):

    articles = []

    for nom in selection:

        requete = mots_cles_news.get(nom, nom + " action bourse")

        url = (

            "https://news.google.com/rss/search?"

            f"q={quote(requete)}"

            "&hl=fr&gl=FR&ceid=FR:fr"

        )

        feed = feedparser.parse(url)

        for entry in feed.entries[:nombre_news]:

            articles.append({

                "Entreprise": nom,

                "Titre": entry.get("title", "Sans titre"),

                "Lien": entry.get("link", "")

            })

    df = pd.DataFrame(articles)

    if not df.empty:

        df = df.drop_duplicates(subset=["Titre"])

        df = df.head(nombre_news)

    return df

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

articles = recuperer_news_fr(selection, nombre_news)

tableau, graph_data = recuperer_donnees(selection, periode)

col_news, col_main = st.columns([0.8, 2.7])

with col_news:

    news_html = """

    <div class="news-box">

        <div class="news-title">📰 News Flow</div>

    """

    if articles.empty:

        news_html += "<p style='color:#94a3b8;font-size:12px;'>Aucune news.</p>"

    else:

        for _, article in articles.iterrows():

            titre = couper_titre(str(article["Titre"]), 50)

            news_html += f"""

            <div class="news-item">

                <a class="news-link" href="{escape(str(article['Lien']))}" target="_blank">

                    <div class="news-company">{escape(str(article['Entreprise']))}</div>

                    <div class="news-headline">{escape(titre)}</div>

                </a>

            </div>

            """

    news_html += "</div>"

    st.markdown(news_html, unsafe_allow_html=True)

with col_main:

    st.title("📊 Dashboard Finance Ionel")

    st.caption("Portefeuille · Watchlist · Données live Yahoo Finance")

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

    c1, c2, c3 = st.columns(3)

    c1.metric(

        "🏆 Meilleure performance",

        leader_perf["Entreprise"],

        f"{leader_perf['Performance (%)']} %"

    )

    c2.metric(

        "💰 Plus grosse capitalisation",

        leader_cap["Entreprise"],

        f"{leader_cap['Cap. boursière (Md$)']:.0f} Md$"

    )

    c3.metric(

        "📈 Meilleure marge nette",

        leader_marge["Entreprise"],

        f"{leader_marge['Marge nette (%)']:.2f} %"

    )

    tab1, tab2, tab3 = st.tabs([

        "📈 Performance",

        "🏦 Fondamentaux",

        "🧠 Synthèse"

    ])

    with tab1:

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

        st.dataframe(

            tableau,

            use_container_width=True

        )

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

        st.success(

            f"{leader_perf['Entreprise']} affiche la meilleure dynamique boursière du panier "

            f"avec une performance de {leader_perf['Performance (%)']} % sur la période."

        )

        st.info(

            f"{leader_cap['Entreprise']} domine le panier en taille de marché "

            f"avec une capitalisation d’environ {leader_cap['Cap. boursière (Md$)']:.0f} Md$."

        )

        st.warning(

            "Prochaine étape : séparer Portefeuille et Watchlist, puis ajouter un score d’attractivité "

            "avec ROIC, dette nette, croissance, valorisation, moat et newsflow."

        )
