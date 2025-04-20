import streamlit as st
import json
import pandas as pd
from datetime import datetime, date
import pytz

#définir le fuseau horaire
tz = pytz.timezone("Europe/Paris")
# Charger les données depuis le fichier JSON (si le fichier existe)
try:
    with open('carburant.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    data = []

# Titre
st.title("🚐 Journal de pleins - Camping-car")

# Formulaire pour ajouter un plein
with st.form("plein_form"):
    col1, col2 = st.columns(2)
    with col1:
        date_plein = st.date_input("📅 Date du plein", date.today())
        kilometrage = st.number_input("Kilométrage", min_value=0, step=1)
    with col2:
        type_plein = st.selectbox("Type de plein", ["Diesel", "AdBlue"])
        litres = st.number_input("Litres", min_value=0.0, step=0.1)

    submitted = st.form_submit_button("Ajouter le plein")
    
if submitted:
    if kilometrage <= 0 or litres <= 0:
        st.error("❌ Veuillez entrer un kilométrage et une quantité de litres valides (supérieurs à 0).")
    else:
        now = datetime.now(tz)
        datetime_plein = datetime.combine(date_plein, now.time(),tzinfo=tz)
        nouveau_plein = {
            "date": str(datetime_plein),  # contient heure avec microsecondes
            "kilometrage": kilometrage,
            "type": type_plein,
            "litres": litres
    }
    data.append(nouveau_plein)

    with open('carburant.json', 'w') as f:
        json.dump(data, f)

    st.success("✅ Plein enregistré avec succès !")

# Affichage des données
st.subheader("📜 Historique des pleins")
if data:
    df = pd.DataFrame(data)

    # Correction du parsing de date
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M:%S.%f")
    df = df.sort_values("date")

    st.markdown(f"**📅 Dernier plein enregistré :** {df['date'].max().strftime('%Y-%m-%d %H:%M')}")

    st.dataframe(df)

    st.subheader("📊 Visualisation des données")
    type_affichage = st.selectbox("Afficher les graphiques pour :", ["Diesel", "AdBlue"], index=0)
    filtre = df[df["type"] == type_affichage]

    if not filtre.empty:
        st.line_chart(filtre.set_index("date")["litres"])

        if type_affichage == "Diesel" and len(filtre) >= 2:
            filtre = filtre.dropna(subset=["kilometrage", "litres"])
            filtre = filtre.sort_values("kilometrage")
            conso = []
            for i in range(1, len(filtre)):
                km_diff = filtre.iloc[i]["kilometrage"] - filtre.iloc[i-1]["kilometrage"]
                litres = filtre.iloc[i]["litres"]
                if km_diff > 0:
                    conso.append((filtre.iloc[i]["date"], (litres / km_diff) * 100))
            if conso:
                conso_df = pd.DataFrame(conso, columns=["date", "Conso L/100km"])
                conso_df = conso_df.set_index("date")
                st.line_chart(conso_df)
            else:
                st.info("Pas assez de données pour calculer la consommation.")
    else:
        st.warning("Aucune donnée pour ce type de plein.")