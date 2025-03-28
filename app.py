import streamlit as st
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from googletrans import Translator
from fpdf import FPDF
import tempfile
import os

# Configuración OCR
pytesseract.pytesseract.tesseract_cmd = "tesseract"
ocr_config = r'--oem 3 --psm 6 -l spa'

translator = Translator()

# Función para generar el PDF traducido
def crear_pdf(texto_ocr, traduccion):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Texto original:\n{texto_ocr}\n\n--- Traducción ---\n{traduccion}")
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)
    return temp_pdf.name

# Interfaz de usuario
st.set_page_config(page_title="Indexador FamilySearch con Traducción", layout="centered")
st.title("📜 Traductor de Registros para Indexación")
st.markdown("Pegá el enlace del lote de FamilySearch y subí tu imagen o PDF escaneado.")

st.markdown("Pegá el enlace del lote de FamilySearch y subí tu imagen o PDF escaneado.")

lote_url = st.text_input("🔗 Enlace del lote (opcional):", "")

archivo = st.file_uploader("📎 Subí una imagen o PDF", type=["png", "jpg", "jpeg", "pdf"])

# 👉 Mostrar ayuda si pegó el link pero no subió imagen
if lote_url and not archivo:
    st.warning("⚠️ **No se puede descargar directamente desde FamilySearch.**")

    st.info("### 🧾 ¿Qué podés hacer?\n"
            "FamilySearch bloquea la descarga directa desde su visor de indexación. Pero podés usar una captura de pantalla.\n\n"
            "### 🖼️ ¿Cómo tomar una captura?\n"
            "**Windows** 🪟:\n"
            "- Presioná `Windows + Shift + S`\n"
            "- Seleccioná el área de la imagen\n"
            "- Guardala como `.png` o `.jpg`\n\n"
            "**Mac** 🍏:\n"
            "- Presioná `Cmd + Shift + 4`\n"
            "- Seleccioná el área de la imagen\n\n"
            "### ✅ Luego:\n"
            "- Volvé a esta app\n"
            "- Subí la imagen capturada abajo 📤\n\n"
            "**¡Y listo! La app hará el OCR y la traducción automáticamente.**")


if archivo is not None:
    st.info("Procesando archivo...")
    texto_extraido = ""

    if archivo.type == "application/pdf":
        imagenes = convert_from_bytes(archivo.read())
    else:
        imagenes = [Image.open(archivo)]

    for img in imagenes:
        texto_extraido += pytesseract.image_to_string(img, config=ocr_config) + "\n"

    st.subheader("📜 Texto detectado:")
    st.text_area("Texto OCR:", value=texto_extraido.strip(), height=250)

    traduccion = translator.translate(texto_extraido, src='es', dest='en').text

    st.subheader("🌍 Traducción al inglés:")
    st.text_area("Traducción:", value=traduccion.strip(), height=250)

    if st.button("📄 Descargar PDF con traducción"):
        pdf_path = crear_pdf(texto_extraido, traduccion)
        with open(pdf_path, "rb") as f:
            st.download_button("Descargar PDF", f, file_name="registro_traducido.pdf")
        os.unlink(pdf_path)
