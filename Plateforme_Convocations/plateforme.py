import streamlit as st
import PyPDF2
import io
import base64
import os

# Configuration de la page
st.set_page_config(page_title="Convocation Examens", page_icon="🎓", layout="centered")

# ==========================================
# 🔐 ESPACE ADMINISTRATEUR (Barre latérale)
# ==========================================
with st.sidebar:
    st.header("⚙️ Espace Administrateur")
    st.write("Réservé à l'administration.")
    
    # Mot de passe pour afficher la zone d'importation
    admin_password = st.text_input("Mot de passe :", type="password")
    
    # Change "admin123" par le mot de passe secret de ton choix !
    if admin_password == "admin123":
        st.success("Authentification réussie.")
        uploaded_file = st.file_uploader("Importez le fichier PDF global", type="pdf")
        
        # Si un fichier est chargé, on le sauvegarde sur le serveur
        if uploaded_file is not None:
            with open("fichier_convocations_serveur.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("✅ Fichier sauvegardé sur le serveur ! Les étudiants peuvent maintenant chercher leur convocation.")


# ==========================================
# 🎓 ESPACE ÉTUDIANT (Page principale)
# ==========================================
st.title("🎓 Plateforme de Retrait des Convocations")
st.write("Bienvenue ! Veuillez entrer votre numéro d'étudiant pour consulter et télécharger votre convocation aux examens.")

student_id = st.text_input("Numéro d'étudiant :", placeholder="Ex: 10000509")

# Fonction pour afficher le PDF sur la page web
def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

if st.button("Rechercher ma convocation"):
    # On vérifie si l'administrateur a bien sauvegardé le fichier sur le serveur
    if not os.path.exists("fichier_convocations_serveur.pdf"):
        st.warning("⚠️ Les convocations ne sont pas encore disponibles. L'administration n'a pas encore chargé le fichier.")
    elif not student_id:
        st.warning("⚠️ Veuillez entrer un numéro d'étudiant valide.")
    else:
        with st.spinner("Recherche de votre convocation en cours..."):
            try:
                # On ouvre le fichier qui est sauvegardé sur le serveur
                with open("fichier_convocations_serveur.pdf", "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    found = False
                    
                    # Recherche du numéro dans chaque page
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        # Si le numéro d'étudiant est trouvé
                        if text and str(student_id) in text:
                            found = True
                            
                            pdf_writer = PyPDF2.PdfWriter()
                            pdf_writer.add_page(page)
                            
                            output_pdf = io.BytesIO()
                            pdf_writer.write(output_pdf)
                            output_pdf.seek(0)
                            pdf_bytes = output_pdf.read()
                            
                            st.success("✅ Convocation trouvée !")
                            
                            st.download_button(
                                label="📥 Télécharger ma convocation (PDF)",
                                data=pdf_bytes,
                                file_name=f"Convocation_{student_id}.pdf",
                                mime="application/pdf"
                            )
                            
                            st.markdown("### Aperçu de votre convocation :")
                            display_pdf(pdf_bytes)
                            
                            break # On arrête la recherche dès qu'on a trouvé
                    
                    if not found:
                        st.error("❌ Aucune convocation trouvée pour ce numéro d'étudiant. Veuillez vérifier votre saisie.")
                        
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de la lecture du fichier : {e}")