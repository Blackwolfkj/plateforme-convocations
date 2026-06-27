import streamlit as st
import PyPDF2
import io
import base64

# Configuration de la page
st.set_page_config(page_title="Convocation Examens", page_icon="🎓", layout="centered")

st.title("🎓 Plateforme de Retrait des Convocations")
st.write("Bienvenue ! Veuillez entrer votre numéro d'étudiant pour consulter et télécharger votre convocation aux examens.")

# Zone d'importation du PDF
uploaded_file = st.file_uploader("Administrateur : Importez le fichier 'convocations_etudiants.pdf'", type="pdf")

st.divider()

# Zone de recherche pour l'étudiant
student_id = st.text_input("Numéro d'étudiant :", placeholder="Ex: 10000509")

# Fonction pour afficher le PDF sur la page web
def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    # Intégration du PDF en HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

if st.button("Rechercher ma convocation"):
    if not uploaded_file:
        st.warning("⚠️ Le fichier des convocations n'a pas encore été chargé par l'administration.")
    elif not student_id:
        st.warning("⚠️ Veuillez entrer un numéro d'étudiant valide.")
    else:
        with st.spinner("Recherche de votre convocation en cours..."):
            try:
                # Lecture du PDF global
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                found = False
                
                # Recherche du numéro dans chaque page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Si le numéro d'étudiant est trouvé
                    if text and str(student_id) in text:
                        found = True
                        
                        # 1. On crée un nouveau fichier PDF en mémoire contenant juste cette page
                        pdf_writer = PyPDF2.PdfWriter()
                        pdf_writer.add_page(page)
                        
                        output_pdf = io.BytesIO()
                        pdf_writer.write(output_pdf)
                        output_pdf.seek(0)
                        pdf_bytes = output_pdf.read()
                        
                        st.success("✅ Convocation trouvée !")
                        
                        # 2. On affiche le bouton pour télécharger UNIQUEMENT cette page
                        st.download_button(
                            label="📥 Télécharger ma convocation (PDF)",
                            data=pdf_bytes,
                            file_name=f"Convocation_{student_id}.pdf",
                            mime="application/pdf"
                        )
                        
                        # 3. On affiche la page PDF originale directement sur le site
                        st.markdown("### Aperçu de votre convocation :")
                        display_pdf(pdf_bytes)
                        
                        break # On a trouvé l'étudiant, on arrête de chercher
                
                if not found:
                    st.error("❌ Aucune convocation trouvée pour ce numéro d'étudiant. Veuillez vérifier votre saisie.")
                    
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de la lecture du fichier : {e}")