import streamlit as st

import streamlit.components.v1 as components

import yfinance as yf

import pandas as pd

import plotly.express as px

import feedparser

from urllib.parse import quote

from html import escape

from datetime import datetime, time

from zoneinfo import ZoneInfo

st.set_page_config(

    page_title="Dashboard Finance Ionel",

    layout="wide",

    page_icon="📊"

)

actions_disponibles = {

    "Apple": "AAPL",

    "Nvidia": "NVDA",

    "ASML": "ASML",

    "LVMH": "MC.PA"

}

portefeuille_simule = {

    "Apple": {"quantite": 10, "prix_achat": 180},

    "Nvidia": {"quantite": 8, "prix_achat": 105},

    "ASML": {"quantite": 3, "prix_achat": 720},

    "LVMH": {"quantite": 4, "prix_achat": 690}

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

    "LVMH": "LVMH action bourse luxe"

}

with st.sidebar:

    st.header("⚙️ Navigation")

    page = st.radio(

        "Menu",

        [

            "Accueil",

            "Univers Apple",

            "Univers Nvidia",

            "Univers ASML",

            "Univers LVMH"

        ]

    )

    st.divider()

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

def marche_paris_ouverte():

    maintenant = datetime.now(ZoneInfo("Europe/Paris"))

    if maintenant.weekday() >= 5:

        return False

    return time(9, 0) <= maintenant.time() <= time(17, 30)

@st.cache_data(ttl=60)

def recuperer_indices():

    resultats = []

    for nom, ticker in indices_marche.items():

        action = yf.Ticker(ticker)

        if nom == "CAC 40" and not marche_paris_ouverte():

            daily = action.history(period="5d", interval="1d")

            if daily.empty or len(daily["Close"].dropna()) < 2:

                continue

            close_values = daily["Close"].dropna()

            dernier = close_values.iloc[-1]

            previous_close = close_values.iloc[-2]

        else:

            data = action.history(period="1d", interval="1m")

            info = action.info

            if data.empty:

                continue

            dernier = data["Close"].dropna().iloc[-1]

            previous_close = info.get("previousClose")

            if previous_close is None:

                hist = action.history(period="5d", interval="1d")

                if len(hist["Close"].dropna()) >= 2:

                    previous_close = hist["Close"].dropna().iloc[-2]

                else:

                    previous_close = data["Close"].dropna().iloc[0]

        variation = round((dernier / previous_close - 1) * 100, 2)

        resultats.append({

            "Nom": nom,

            "Cours": round(dernier, 2),

            "Variation": variation

        })

    return resultats

def couper_titre(titre, longueur=55):

    if len(titre) <= longueur:

        return titre

    return titre[:longueur] + "..."

def analyser_news(titre):

    texte = titre.lower()

    positifs = ["hausse", "progresse", "croissance", "record", "relève", "bénéfice", "profit", "contrat", "demande", "forte"]

    negatifs = ["baisse", "chute", "recul", "ralentissement", "pression", "perte", "déçoit", "alerte", "risque", "crise"]

    resultats = ["résultats", "trimestriel", "bénéfice", "chiffre d'affaires", "marge", "guidance", "prévisions"]

    buzz = ["ia", "intelligence artificielle", "puce", "semi-conducteurs", "chine", "luxe", "analyste", "objectif de cours"]

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

def recuperer_donnees(periode):

    resultats = []

    courbes = []

    for nom, ticker in actions_disponibles.items():

        action = yf.Ticker(ticker)

        data = action.history(period=periode)

        info = action.info

        if data.empty:

            continue

        prix = round(data["Close"].iloc[-1], 2)

        performance = round((data["Close"].iloc[-1] / data["Close"].iloc[0] - 1) * 100, 2)

        position = portefeuille_simule[nom]

        quantite = position["quantite"]

        prix_achat = position["prix_achat"]

        valeur_actuelle = round(quantite * prix, 2)

        montant_investi = round(quantite * prix_achat, 2)

        gain_perte = round(valeur_actuelle - montant_investi, 2)

        gain_perte_pct = round((valeur_actuelle / montant_investi - 1) * 100, 2)

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

            "Perf. marché (%)": performance,

            "Quantité": quantite,

            "Prix achat": prix_achat,

            "Montant investi": montant_investi,

            "Valeur actuelle": valeur_actuelle,

            "Gain/Perte": gain_perte,

            "Gain/Perte (%)": gain_perte_pct,

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

articles = recuperer_news_fr(list(actions_disponibles.keys()), nombre_news)

tableau, graph_data = recuperer_donnees(periode)

if tableau.empty:

    st.warning("Aucune donnée disponible.")

    st.stop()

st.markdown("## 🌍 Marchés en direct")

cols_indices = st.columns(3)

for col, indice in zip(cols_indices, indices):

    col.metric(

        label=indice["Nom"],

        value=f"{indice['Cours']:.2f}",

        delta=f"{indice['Variation']:.2f} %"

    )

st.divider()

if page == "Accueil":

    col_news, col_main = st.columns([0.9, 2.6])

    with col_news:

        st.markdown("### 📰 News Flow")

        societe_news = st.selectbox(

            "Société",

            list(actions_disponibles.keys()),

            index=0

        )

        filtre_news = st.selectbox(

            "Filtre",

            ["Toutes", "Positives", "Négatives", "Résultats trimestriels", "Buzz / Thématique"]

        )

        news_filtrees = articles[articles["Entreprise"] == societe_news]

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

        st.caption("Accueil · Vue portefeuille simulée · Watchlist à venir")

        total_investi = tableau["Montant investi"].sum()

        total_valeur = tableau["Valeur actuelle"].sum()

        gain_total = total_valeur - total_investi

        perf_portefeuille = (total_valeur / total_investi - 1) * 100

        meilleure_ligne = tableau.sort_values(by="Gain/Perte (%)", ascending=False).iloc[0]

        pire_ligne = tableau.sort_values(by="Gain/Perte (%)", ascending=True).iloc[0]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(

            "💼 Valeur portefeuille",

            f"{total_valeur:,.0f} $",

            f"{perf_portefeuille:.2f} %"

        )

        c2.metric(

            "💰 Gain / perte total",

            f"{gain_total:,.0f} $"

        )

        c3.metric(

            "🏆 Meilleure ligne",

            meilleure_ligne["Entreprise"],

            f"{meilleure_ligne['Gain/Perte (%)']:.2f} %"

        )

        c4.metric(

            "⚠️ Ligne à surveiller",

            pire_ligne["Entreprise"],

            f"{pire_ligne['Gain/Perte (%)']:.2f} %"

        )

        st.subheader("📈 Performance relative des actions")

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

            height=520,

            hovermode="x unified"

        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🏦 Vue portefeuille simulée")

        colonnes_home = [

            "Entreprise",

            "Quantité",

            "Prix achat",

            "Prix",

            "Montant investi",

            "Valeur actuelle",

            "Gain/Perte",

            "Gain/Perte (%)"

        ]

        st.dataframe(

            tableau[colonnes_home],

            use_container_width=True

        )

else:

    nom_action = page.replace("Univers ", "")

    ligne = tableau[tableau["Entreprise"] == nom_action].iloc[0]

    articles_action = articles[articles["Entreprise"] == nom_action]

    st.title(f"🌐 Univers {nom_action}")

    st.caption("Fiche action individuelle · Version simple")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Prix actuel", f"{ligne['Prix']:.2f}")

    c2.metric("Perf. marché", f"{ligne['Perf. marché (%)']:.2f} %")

    c3.metric("Gain/Perte position", f"{ligne['Gain/Perte']:.0f} $", f"{ligne['Gain/Perte (%)']:.2f} %")

    c4.metric("PER", f"{ligne['PER']:.2f}" if pd.notna(ligne["PER"]) else "N/A")

    tab1, tab2, tab3 = st.tabs(["📈 Cours", "🏦 Fondamentaux", "📰 News"])

    with tab1:

        data_action = graph_data[graph_data["Entreprise"] == nom_action]

        fig_action = px.line(

            data_action,

            x="Date",

            y="Performance base 100",

            markers=True,

            title=f"{nom_action} — Performance base 100 sur {periode}"

        )

        fig_action.update_layout(

            template="plotly_dark",

            height=520

        )

        st.plotly_chart(fig_action, use_container_width=True)

    with tab2:

        st.dataframe(

            pd.DataFrame([ligne]),

            use_container_width=True

        )

    with tab3:

        if articles_action.empty:

            st.warning("Aucune news disponible.")

        else:

            for _, article in articles_action.head(10).iterrows():

                st.markdown(f"### {article['Titre']}")

                st.caption(f"{article['Tonalité']} · {article['Catégorie']} · Score IA {article['Score IA']}/10")

                st.link_button("Lire l'article", article["Lien"])
