import streamlit as st
import json
import pandas as pd
from datetime import datetime, date

# Charger les données depuis le fichier JSON (si le fichier existe)
try:
    with open('carburant.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    data = []

# Formulaire pour ajouter un plein
st.title("🚐 Journal de pleins - Camping-car")

with st.form("plein_form"):
    col1, col2 = st.columns(2)
    with col1:
        date_plein = st.date_input("📅 Date du plein", date.today())
        kilometrage = st.number_input("Kilométrage", min_value=0, step=1)
    with col2:
        type_plein = st.selectbox("Type de plein", ["Diesel", "AdBlue"])
        litres = st.number_input("Litres", min_value=0.0, step=0.1)

    # Désactiver le bouton si kilométrage ou litres ne sont pas remplis
    is_disabled = kilometrage == None or litres == None
    submitted = st.form_submit_button("Ajouter le plein", disabled=is_disabled)

if submitted:
    now = datetime.now()
    datetime_plein = datetime.combine(date_plein, now.time())
    nouveau_plein = {
        "date": datetime_plein.isoformat(),  # Format ISO pour éviter les erreurs
        "kilometrage": kilometrage,
        "type": type_plein,
        "litres": litres,
    }
    data.append(nouveau_plein)

    with open('carburant.json', 'w') as f:
        json.dump(data, f)

    st.success("✅ Plein enregistré avec succès !")

# Affichage des données
st.subheader("📜 Historique des pleins")
if data:
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"], format="ISO8601", errors='coerce')
    df = df.sort_values("date")

    st.markdown(f"**📅 Dernier plein enregistré :** {df['date'].max().strftime('%Y-%m-%d %H:%M')}")

    st.dataframe(df)

    st.subheader("📊 Visualisation des données")

    type_affichage = st.selectbox("Afficher les graphiques pour :", ["Diesel", "AdBlue"], index=0)

    filtre = df[df["type"] == type_affichage]

    if not filtre.empty:
        st.line_chart(filtre.set_index("date")["litres"])

        if type_affichage == "Diesel" and len(filtre) >= 2:
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
