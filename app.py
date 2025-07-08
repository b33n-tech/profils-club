import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Extracteur de Profils", layout="centered")
st.title("🧹 Extracteur de Profils - Nom + Entreprise")

# Étape 1 : Choix du nombre de pages
nb_pages = st.number_input("Combien de pages à traiter ? (10 profils/page)", min_value=1, step=1, key="nb_pages")

# Réinitialisation manuelle
if st.button("🔁 Réinitialiser l'import"):
    st.session_state.clear()
    st.rerun()

# Initialisation des variables de session
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
if "all_texts" not in st.session_state:
    st.session_state.all_texts = []

# Affichage de la barre de progression
progress = st.progress((st.session_state.current_page - 1) / nb_pages)
st.write(f"Page {st.session_state.current_page} sur {nb_pages}")

# Zone de texte pour coller les profils
texte_page = st.text_area(f"📋 Colle ici les profils de la page {st.session_state.current_page} :", height=300)

# Bouton pour passer à la page suivante
if st.button("➡️ Importer cette page et passer à la suivante"):
    if texte_page.strip():
        st.session_state.all_texts.append(texte_page)
        if st.session_state.current_page < nb_pages:
            st.session_state.current_page += 1
            st.rerun()
        else:
            st.success("🎉 Toutes les pages ont été importées !")
    else:
        st.error("⛔ Merci de coller les données avant de continuer.")

# Traitement final une fois toutes les pages importées
if len(st.session_state.all_texts) == nb_pages:

    def parser_profils(texte_total):
        lignes = [l.strip() for l in texte_total.split("\n") if l.strip()]
        blocs = []
        bloc = []

        for ligne in lignes:
            bloc.append(ligne)
            if re.match(r"\d{2}/\d{2}/\d{4}", ligne):  # Fin du bloc détectée
                blocs.append(bloc)
                bloc = []

        if bloc:
            blocs.append(bloc)

        profils = []
        for bloc in blocs:
            if len(bloc) >= 3:
                nom = bloc[1]
                entreprise = bloc[2]
                profils.append((nom, entreprise))
        return profils

    texte_total = "\n".join(st.session_state.all_texts)
    profils = parser_profils(texte_total)

    df = pd.DataFrame(profils, columns=["Nom complet", "Entreprise"])
    st.success(f"{len(df)} profils extraits automatiquement ✅")

    # Retouche manuelle via éditeur interactif
    st.subheader("✏️ Retouches manuelles (optionnelles)")
    st.markdown("👉 Tu peux modifier les noms ou entreprises directement dans le tableau ci-dessous avant d’exporter.")

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True
    )

    # Export Excel
    st.subheader("📦 Export Excel")
    if st.button("📤 Générer et télécharger le fichier Excel"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            edited_df.to_excel(writer, index=False, sheet_name='Profils')
        output.seek(0)

        st.download_button(
            label="📥 Télécharger le fichier Excel",
            data=output,
            file_name="profils_corrigés.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
