import streamlit as st

import streamlit.components.v1 as components

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

indices_marche = {

    "CAC 40": "^FCHI",

    "S&P 500": "^GSPC",

    "Nasdaq": "^IXIC"

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

st.markdown("""

<style>

.market-wrapper {

    max-width: 1050px;

    margin: 0 auto 24px auto;

}

.market-title {

    text-align: center;

    font-size: 26px;

    font-weight: 800;

    margin-bottom: 18px;

}

.market-grid {

    display: grid;

    grid-template-columns: repeat(3, 1fr);

    gap: 18px;

}

.market-card {

    background: linear-gradient(135deg, #0f172a, #111827);

    border: 1px solid #334155;

    border-radius: 18px;

    padding: 20px;

    text-align: center;

    box-shadow: 0 12px 30px rgba(0,0,0,0.22);

}

.market-name {

    color: #94a3b8;

    font-size: 13px;

    font-weight: 700;

    text-transform: uppercase;

    margin-bottom: 8px;

}

.market-price {

    color: #f8fafc;

    font-size: 28px;

    font-weight: 900;

    margin-bottom: 6px;

}

.market-var-positive {

    color: #22c55e;

    font-size: 20px;

    font-weight: 900;

}

.market-var-negative {

    color: #ef4444;

    font-size: 20px;

    font-weight: 900;

}

.market-var-neutral {

    color: #94a3b8;

    font-size: 20px;

    font-weight: 900;

}

@media (max-width: 800px) {

    .market-grid {

        grid-template-columns: 1fr;

    }

}

</style>

""", unsafe_allow_html=True)

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

        "Nombre d'articles analysés",

        5,

        40,

        20

    )

    if st.button("🔄 Rafraîchir"):

        st.cache_data.clear()

@st.cache_data(ttl=60)

def recuperer_indices():

    resultats = []

    for nom, ticker in indices_marche.items():

        action = yf.Ticker(ticker)

        data = action.history(

            period="1d",

            interval="1m"

        )

        info = action.info

        if data.empty:

            continue

        dernier = data["Close"].dropna().iloc[-1]

        previous_close = info.get("previousClose")

        if previous_close is None:

            previous_close = data["Close"].dropna().iloc[0]

        variation = round(

            (dernier / previous_close - 1) * 100,

            2

        )

        resultats.append({

            "Nom": nom,

            "Cours": round(dernier, 2),

            "Variation": variation

        })

    return resultats

def afficher_bandeau_indices(indices):

    html = """

    <div class="market-wrapper">

        <div class="market-title">🌍 Marchés en direct</div>

        <div class="market-grid">

    """

    for indice in indices:

        variation = indice["Variation"]

        if variation > 0:

            classe = "market-var-positive"

            signe = "+"

        elif variation < 0:

            classe = "market-var-negative"

            signe = ""

        else:

            classe = "market-var-neutral"

            signe = ""

        html += f"""

        <div class="market-card">

            <div class="market-name">{indice["Nom"]}</div>

            <div class="market-price">{indice["Cours"]:.2f}</div>

            <div class="{classe}">{signe}{variation:.2f}%</div>

        </div>

        """

    html += """

        </div>

    </div>

    """

    st.markdown(html, unsafe_allow_html=True)

def couper_titre(titre, longueur=55):

    if len(titre) <= longueur:

        return titre

    return titre[:longueur] + "..."

def analyser_news(titre):

    texte = titre.lower()

    positifs = [

        "hausse", "progresse", "croissance", "record", "relève",

        "boost", "bénéfice", "profit", "surperformance", "optimiste",

        "accord", "contrat", "demande", "forte", "augmentation"

    ]

    negatifs = [

        "baisse", "chute", "recul", "ralentissement", "pression",

        "perte", "déçoit", "alerte", "risque", "faible",

        "pénalisé", "enquête", "amende", "crise", "inquiétude"

    ]

    resultats = [

        "résultats", "trimestriel", "trimestriels", "bénéfice",

        "chiffre d'affaires", "ca", "marge", "guidance", "prévisions"

    ]

    buzz = [

        "ia", "intelligence artificielle", "puce", "semi-conducteurs",

        "chine", "luxe", "innovation", "breaking", "urgent",

        "analyste", "objectif de cours"

    ]

    score = 0

    categorie = "Neutre"

    for mot in positifs:

        if mot in texte:

            score += 2

    for mot in negatifs:

        if mot in texte:

            score -= 2

    if any(mot in texte for mot in resultats):

        categorie = "Résultats trimestriels"

    elif any(mot in texte for mot in buzz):

        categorie = "Buzz / Thématique"

    if score > 0:

        tonalite = "Positive"

    elif score < 0:

        tonalite = "Négative"

    else:

        tonalite = "Neutre"

    score_ia = max(-10, min(10, score))

    return tonalite, categorie, score_ia

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

            titre = entry.get("title", "Sans titre")

            tonalite, categorie, score_ia = analyser_news(titre)

            articles.append({

                "Entreprise": nom,

                "Titre": titre,

                "Lien": entry.get("link", ""),

                "Tonalité": tonalite,

                "Catégorie": categorie,

                "Score IA": score_ia

            })

    df = pd.DataFrame(articles)

    if not df.empty:

        df = df.drop_duplicates(subset=["Titre"])

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

indices = recuperer_indices()

articles = recuperer_news_fr(selection, nombre_news)

tableau, graph_data = recuperer_donnees(selection, periode)

afficher_bandeau_indices(indices)

st.divider()

col_news, col_main = st.columns([0.9, 2.6])

with col_news:

    st.markdown("### 📰 News Flow")

    societe_news = st.selectbox(

        "Société",

        selection,

        index=0

    )

    filtre_news = st.selectbox(

        "Filtre",

        [

            "Toutes",

            "Positives",

            "Négatives",

            "Résultats trimestriels",

            "Buzz / Thématique"

        ]

    )

    news_filtrees = articles[

        articles["Entreprise"] == societe_news

    ]

    if filtre_news == "Positives":

        news_filtrees = news_filtrees[news_filtrees["Tonalité"] == "Positive"]

    elif filtre_news == "Négatives":

        news_filtrees = news_filtrees[news_filtrees["Tonalité"] == "Négative"]

    elif filtre_news == "Résultats trimestriels":

        news_filtrees = news_filtrees[news_filtrees["Catégorie"] == "Résultats trimestriels"]

    elif filtre_news == "Buzz / Thématique":

        news_filtrees = news_filtrees[news_filtrees["Catégorie"] == "Buzz / Thématique"]

    news_html = """

    <style>

    .news-box {

        background: #0f172a;

        border: 1px solid #334155;

        border-radius: 14px;

        padding: 12px;

        height: 360px;

        overflow-y: auto;

        font-family: Arial, sans-serif;

    }

    .news-item {

        padding: 9px 0;

        border-bottom: 1px solid #334155;

    }

    .company {

        color: #38bdf8;

        font-size: 11px;

        font-weight: 800;

    }

    .headline {

        color: #f8fafc;

        font-size: 12px;

        font-weight: 700;

        line-height: 1.25;

    }

    .meta {

        font-size: 11px;

        margin-top: 4px;

    }

    .positive { color: #22c55e; }

    .negative { color: #ef4444; }

    .neutral { color: #94a3b8; }

    a {

        text-decoration: none;

    }

    </style>

    <div class="news-box">

    """

    if news_filtrees.empty:

        news_html += "<p style='color:#94a3b8;font-size:12px;'>Aucune news pour ce filtre.</p>"

    else:

        for _, article in news_filtrees.iterrows():

            titre = couper_titre(str(article["Titre"]), 55)

            tonalite = article["Tonalité"]

            classe = "neutral"

            if tonalite == "Positive":

                classe = "positive"

            elif tonalite == "Négative":

                classe = "negative"

            news_html += f"""

            <div class="news-item">

                <a href="{escape(str(article['Lien']))}" target="_blank">

                    <div class="company">{escape(str(article['Entreprise']))}</div>

                    <div class="headline">{escape(titre)}</div>

                    <div class="meta {classe}">

                        {escape(str(article['Tonalité']))} · {escape(str(article['Catégorie']))} · Score IA {article['Score IA']}/10

                    </div>

                </a>

            </div>

            """

    news_html += "</div>"

    components.html(

        news_html,

        height=390,

        scrolling=True

    )

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

            "Prochaine étape : portefeuille/watchlist séparés, scoring plus fin, ROIC et dette nette."

        )
