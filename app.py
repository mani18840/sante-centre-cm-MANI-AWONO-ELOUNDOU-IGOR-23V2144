import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import initialiser_base, get_tous_hopitaux, enregistrer_avis, get_tous_avis

# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="SantéCentre CM",
    page_icon="🏥",
    layout="wide"
)

# ── Initialisation de la base ─────────────────────────────────────────────────
initialiser_base()

# ── Style CSS personnalisé ────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1a6b3c;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #555;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f7f4;
        border-left: 4px solid #1a6b3c;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .rank-gold   { color: #FFD700; font-size: 1.3rem; }
    .rank-silver { color: #C0C0C0; font-size: 1.3rem; }
    .rank-bronze { color: #CD7F32; font-size: 1.3rem; }
    .success-box {
        background: #d4edda;
        border: 1px solid #1a6b3c;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        font-size: 1.1rem;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

# ── En-tête ───────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">🏥 SantéCentre Cameroun</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Plateforme d\'évaluation des hôpitaux de la Région du Centre</p>', unsafe_allow_html=True)
st.divider()

# ── Navigation ────────────────────────────────────────────────────────────────
onglet1, onglet2, onglet3 = st.tabs([
    "📝 Donner mon avis",
    "📊 Classement & Analyses",
    "📋 Tous les avis"
])

# ════════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — FORMULAIRE DE COLLECTE
# ════════════════════════════════════════════════════════════════════════════════
with onglet1:
    st.subheader("Évaluez un hôpital de la Région du Centre")
    st.write("Votre avis aide les populations à choisir les meilleurs soins. Merci pour votre contribution !")

    hopitaux = get_tous_hopitaux()
    noms_hopitaux = {h[1]: h[0] for h in hopitaux}

    with st.form("formulaire_avis", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            nom_patient = st.text_input("👤 Votre prénom (ou anonyme)", placeholder="Ex: Marie ou Anonyme")
            hopital_choisi = st.selectbox("🏥 Hôpital visité", list(noms_hopitaux.keys()))

        with col2:
            st.markdown("**📅 Date de votre visite**")
            st.write("_(La date d'aujourd'hui sera enregistrée automatiquement)_")

        st.markdown("---")
        st.markdown("### ⭐ Notez les critères suivants (1 = Très mauvais / 5 = Excellent)")

        col3, col4 = st.columns(2)
        with col3:
            note_soins = st.slider("💊 Qualité des soins", 1, 5, 3)
            note_hygiene = st.slider("🧼 Hygiène et propreté", 1, 5, 3)
        with col4:
            note_accueil = st.slider("😊 Accueil du personnel", 1, 5, 3)
            note_infrastructure = st.slider("🏗️ Infrastructure et équipements", 1, 5, 3)

        commentaire = st.text_area(
            "💬 Commentaire libre (optionnel)",
            placeholder="Décrivez votre expérience...",
            height=100
        )

        submitted = st.form_submit_button("✅ Soumettre mon évaluation", use_container_width=True)

        if submitted:
            if not nom_patient.strip():
                st.error("⚠️ Veuillez entrer votre prénom ou écrire 'Anonyme'.")
            else:
                hopital_id = noms_hopitaux[hopital_choisi]
                enregistrer_avis(
                    hopital_id, nom_patient.strip(),
                    note_soins, note_hygiene,
                    note_accueil, note_infrastructure,
                    commentaire.strip()
                )
                st.markdown(f"""
                <div class="success-box">
                    🎉 Merci <b>{nom_patient}</b> ! Votre évaluation de <b>{hopital_choisi}</b> a bien été enregistrée.
                </div>
                """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — CLASSEMENT & ANALYSES
# ════════════════════════════════════════════════════════════════════════════════
with onglet2:
    st.subheader("📊 Classement des hôpitaux — Région du Centre")

    avis_data = get_tous_avis()

    if len(avis_data) == 0:
        st.info("📭 Aucun avis enregistré pour l'instant. Soyez le premier à évaluer un hôpital !")
    else:
        df = pd.DataFrame(avis_data, columns=[
            "id", "hopital_id", "nom_patient", "note_soins", "note_hygiene",
            "note_accueil", "note_infrastructure", "commentaire", "date_avis",
            "nom_hopital", "ville", "type_hopital"
        ])

        df["score_global"] = (
            df["note_soins"] + df["note_hygiene"] +
            df["note_accueil"] + df["note_infrastructure"]
        ) / 4

        # ── Statistiques globales ─────────────────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🏥 Hôpitaux évalués", df["nom_hopital"].nunique())
        m2.metric("📝 Total des avis",   len(df))
        m3.metric("⭐ Score moyen",      f"{df['score_global'].mean():.2f} / 5")
        m4.metric("🥇 Meilleur score",   f"{df['score_global'].max():.2f} / 5")

        st.markdown("---")

        # ── Classement général ────────────────────────────────────────────────
        classement = df.groupby("nom_hopital").agg(
            score_global       = ("score_global",       "mean"),
            note_soins         = ("note_soins",         "mean"),
            note_hygiene       = ("note_hygiene",       "mean"),
            note_accueil       = ("note_accueil",       "mean"),
            note_infrastructure= ("note_infrastructure","mean"),
            nb_avis            = ("id",                 "count")
        ).reset_index().sort_values("score_global", ascending=False).reset_index(drop=True)

        classement.index += 1

        medailles = {1: "🥇", 2: "🥈", 3: "🥉"}

        st.markdown("#### 🏆 Classement général")
        for i, row in classement.iterrows():
            med = medailles.get(i, f"#{i}")
            with st.container():
                c1, c2, c3, c4 = st.columns([0.5, 3, 1, 1])
                c1.markdown(f"### {med}")
                c2.markdown(f"**{row['nom_hopital']}**")
                c3.markdown(f"⭐ **{row['score_global']:.2f}** / 5")
                c4.markdown(f"_{int(row['nb_avis'])} avis_")

        st.markdown("---")

        # ── Graphique barres ──────────────────────────────────────────────────
        st.markdown("#### 📊 Comparaison des scores par hôpital")
        fig_bar = px.bar(
            classement.sort_values("score_global"),
            x="score_global",
            y="nom_hopital",
            orientation="h",
            color="score_global",
            color_continuous_scale=["#ff6b6b", "#ffd93d", "#6bcb77"],
            range_color=[1, 5],
            labels={"score_global": "Score moyen", "nom_hopital": "Hôpital"},
            text=classement.sort_values("score_global")["score_global"].apply(lambda x: f"{x:.2f}")
        )
        fig_bar.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="white",
            height=400,
            xaxis=dict(range=[0, 5])
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # ── Radar chart ───────────────────────────────────────────────────────
        st.markdown("#### 🎯 Profil détaillé d'un hôpital")
        hopital_selectionne = st.selectbox(
            "Choisir un hôpital à analyser",
            classement["nom_hopital"].tolist()
        )

        row_h = classement[classement["nom_hopital"] == hopital_selectionne].iloc[0]
        categories = ["Soins", "Hygiène", "Accueil", "Infrastructure"]
        valeurs = [
            row_h["note_soins"],
            row_h["note_hygiene"],
            row_h["note_accueil"],
            row_h["note_infrastructure"]
        ]

        fig_radar = go.Figure(go.Scatterpolar(
            r=valeurs + [valeurs[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(26,107,60,0.2)",
            line=dict(color="#1a6b3c", width=2),
            marker=dict(size=8)
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=False,
            height=400,
            title=f"Profil de {hopital_selectionne}"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # ── Analyse par critère ───────────────────────────────────────────────
        st.markdown("#### 🔍 Comparaison par critère")
        df_criteres = classement[["nom_hopital", "note_soins", "note_hygiene",
                                   "note_accueil", "note_infrastructure"]].melt(
            id_vars="nom_hopital",
            var_name="critere",
            value_name="note"
        )
        df_criteres["critere"] = df_criteres["critere"].replace({
            "note_soins": "Soins",
            "note_hygiene": "Hygiène",
            "note_accueil": "Accueil",
            "note_infrastructure": "Infrastructure"
        })
        fig_grouped = px.bar(
            df_criteres,
            x="nom_hopital",
            y="note",
            color="critere",
            barmode="group",
            labels={"nom_hopital": "Hôpital", "note": "Note moyenne", "critere": "Critère"},
            color_discrete_map={
                "Soins":          "#1a6b3c",
                "Hygiène":        "#2ecc71",
                "Accueil":        "#f39c12",
                "Infrastructure": "#3498db"
            }
        )
        fig_grouped.update_layout(
            plot_bgcolor="white",
            xaxis_tickangle=-30,
            height=420,
            yaxis=dict(range=[0, 5])
        )
        st.plotly_chart(fig_grouped, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — TOUS LES AVIS
# ════════════════════════════════════════════════════════════════════════════════
with onglet3:
    st.subheader("📋 Historique de tous les avis")

    avis_data2 = get_tous_avis()
    if len(avis_data2) == 0:
        st.info("Aucun avis enregistré pour l'instant.")
    else:
        df2 = pd.DataFrame(avis_data2, columns=[
            "id", "hopital_id", "nom_patient", "note_soins", "note_hygiene",
            "note_accueil", "note_infrastructure", "commentaire", "date_avis",
            "nom_hopital", "ville", "type_hopital"
        ])

        # Filtres
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtre_hopital = st.multiselect(
                "Filtrer par hôpital",
                df2["nom_hopital"].unique().tolist(),
                default=df2["nom_hopital"].unique().tolist()
            )
        with col_f2:
            filtre_type = st.multiselect(
                "Filtrer par type",
                df2["type_hopital"].unique().tolist(),
                default=df2["type_hopital"].unique().tolist()
            )

        df2_filtre = df2[
            df2["nom_hopital"].isin(filtre_hopital) &
            df2["type_hopital"].isin(filtre_type)
        ]

        df2_affiche = df2_filtre[[
            "date_avis", "nom_hopital", "ville", "nom_patient",
            "note_soins", "note_hygiene", "note_accueil", "note_infrastructure", "commentaire"
        ]].rename(columns={
            "date_avis":           "Date",
            "nom_hopital":         "Hôpital",
            "ville":               "Ville",
            "nom_patient":         "Patient",
            "note_soins":          "Soins",
            "note_hygiene":        "Hygiène",
            "note_accueil":        "Accueil",
            "note_infrastructure": "Infrastructure",
            "commentaire":         "Commentaire"
        })

        st.dataframe(df2_affiche, use_container_width=True, hide_index=True)
        st.caption(f"Total : {len(df2_filtre)} avis affichés")