import streamlit as st

import yfinance as yf

import pandas as pd

import plotly.express as px

st.set_page_config(

    page_title="Dashboard Investisseur Premium",

    layout="wide"

)

st.title("📊 Dashboard Investisseur Premium")

st.markdown("""

Suivi multi-actifs avec :

- performances

- capitalisations

- PER

- marges

- ROE

- cash-flow

""")

actions = {

    "Apple": "AAPL",

    "Nvidia": "NVDA",

    "ASML": "ASML",

    "LVMH": "MC.PA"

}

resultats = []

courbes = []

for nom, ticker in actions.items():

    action = yf.Ticker(ticker)

    data = action.history(period="1mo")

    info = action.info

    prix = round(

        data["Close"].iloc[-1],

        2

    )

    performance = round(

        (

            data["Close"].iloc[-1]

            /

            data["Close"].iloc[0]

            - 1

        ) * 100,

        2

    )

    market_cap = info.get("marketCap")

    per = info.get("trailingPE")

    marge = info.get("profitMargins")

    roe = info.get("returnOnEquity")

    if market_cap is not None:

        market_cap = round(

            market_cap / 1_000_000_000,

            2

        )

    if marge is not None:

        marge = round(

            marge * 100,

            2

        )

    if roe is not None:

        roe = round(

            roe * 100,

            2

        )

    resultats.append({

        "Entreprise": nom,

        "Prix": prix,

        "Performance 1 mois (%)": performance,

        "Capitalisation (Md$)": market_cap,

        "PER": per,

        "Marge nette (%)": marge,

        "ROE (%)": roe

    })

    data = data.reset_index()

    data["Date"] = pd.to_datetime(

        data["Date"]

    ).dt.tz_localize(None)

    data["Performance base 100"] = (

        data["Close"]

        /

        data["Close"].iloc[0]

    ) * 100

    data["Entreprise"] = nom

    courbes.append(

        data[[

            "Date",

            "Entreprise",

            "Performance base 100"

        ]]

    )

tableau = pd.DataFrame(resultats)

tableau = tableau.sort_values(

    by="Performance 1 mois (%)",

    ascending=False

)

tableau = tableau.reset_index(drop=True)

tableau.index = tableau.index + 1

st.subheader("🏆 Classement des sociétés")

st.dataframe(

    tableau,

    use_container_width=True

)

graph_data = pd.concat(courbes)

fig = px.line(

    graph_data,

    x="Date",

    y="Performance base 100",

    color="Entreprise",

    markers=True,

    title="Performance relative - Base 100"

)

fig.update_layout(

    template="plotly_dark",

    height=600

)

st.plotly_chart(

    fig,

    use_container_width=True

)

leader = tableau.iloc[0]

st.subheader("🧠 Synthèse automatique")

st.success(

    f"{leader['Entreprise']} affiche actuellement la meilleure dynamique boursière du panier avec une performance de {leader['Performance 1 mois (%)']} % sur 1 mois."

)
