import os
import io
import datetime
import streamlit as st
from docxtpl import DocxTemplate

# ------------------------------------------------------------------------------
# CONFIGURAZIONE PAGINA STREAMLIT
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="HR Document Generator - HQE & QTECH",
    page_icon="📄",
    layout="wide"
)

# ------------------------------------------------------------------------------
# ANAGRAFICA AZIENDALE E DEFAULTS
# ------------------------------------------------------------------------------
AZIENDE = {
    "HQ Engineering S.r.l.": {
        "ragione_sociale": "HQ ENGINEERING S.R.L.",
        "piva_cf": "08902230963",
        "indirizzo": "Via G. Stephenson 29, Milano",
        "telefono": "0229062210",
        "fax": "0262690377",
        "ccnl_default": "Terziario Confcommercio (H011)",
        "inps": "Non specificato",
        "inail": "Non specificato",
        "codice_cnel": "H011"
    },
    "QTECH S.r.l.": {
        "ragione_sociale": "QTECH S.R.L.",
        "piva_cf": "06925220961",
        "indirizzo": "Via G. Gentile 7, 20157 Milano",
        "telefono": "0229062210",
        "fax": "0262690377",
        "ccnl_default": "Metalmeccanica Industriale (C011)",
        "inps": "4974532985",
        "inail": "20814097/71",
        "codice_cnel": "C011"
    }
}

# MAPPA DEI DOCUMENTI E RELATIVI TEMPLATE WORD (.docx)
DOCUMENTI_PER_CATEGORIA = {
    "Lavoro Subordinato (Dipendenti)": [
        "Assunzione Tempo Indeterminato",
        "Assunzione Tempo Determinato",
        "Lettera di Intenti Assunzione (+ Penale 10% RAL)",
        "Proroga Tempo Determinato",
        "Cambio Mansione",
        "Trasformazione da Temp. Det. a Indeterminato",
        "Patto di Stabilità (Durata Minima)"
    ],
    "Collaborazioni e Prestazioni Autonome": [
        "Contratto Co.Co.Co. (ex art. 409 c.p.c. / D.Lgs. 81/2015)",
        "Lettera di Intenti Co.Co.Co. (+ Penale 10% RAL)",
        "Proroga Co.Co.Co.",
        "Proroga Co.Co.Co. + Diaria",
        "Contratto d'Opera Intellettuale (P.IVA / Professionista - solo HQE)"
    ]
}

TEMPLATE_MAP = {
    "Assunzione Tempo Indeterminato": "assunzione_indeterminato.docx",
    "Assunzione Tempo Determinato": "assunzione_determinato.docx",
    "Lettera di Intenti Assunzione (+ Penale 10% RAL)": "lettera_intenti_assunzione.docx",
    "Proroga Tempo Determinato": "proroga_determinato.docx",
    "Cambio Mansione": "cambio_mansione.docx",
    "Trasformazione da Temp. Det. a Indeterminato": "trasformazione_indeterminato.docx",
    "Patto di Stabilità (Durata Minima)": "patto_stabilita.docx",
    "Contratto Co.Co.Co. (ex art. 409 c.p.c. / D.Lgs. 81/2015)": "contratto_cococo.docx",
    "Lettera di Intenti Co.Co.Co. (+ Penale 10% RAL)": "lettera_intenti_cococo.docx",
    "Proroga Co.Co.Co.": "proroga_cococo.docx",
    "Proroga Co.Co.Co. + Diaria": "proroga_cococo_diaria.docx",
    "Contratto d'Opera Intellettuale (P.IVA / Professionista - solo HQE)": "opera_intellettuale.docx"
}


# ------------------------------------------------------------------------------
# INTERFACCIA UTENTE
# ------------------------------------------------------------------------------
st.title("📄 HR Document Generator")
st.caption("Generazione automatica dei contratti di lavoro e collaborazioni per HQ Engineering S.r.l. e QTECH S.r.l.")

st.sidebar.header("1. Selezione Azienda")
azienda_scelta = st.sidebar.radio("Seleziona la Società Emittente:", list(AZIENDE.keys()))
dati_azienda = AZIENDE[azienda_scelta]

# Mostra scheda riepilogativa azienda selezionata
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Ragione Sociale:** {dati_azienda['ragione_sociale']}")
st.sidebar.markdown(f"**P.IVA / C.F.:** `{dati_azienda['piva_cf']}`")
st.sidebar.markdown(f"**CCNL Default:** {dati_azienda['ccnl_default']}")
st.sidebar.markdown(f"**POS. INPS:** {dati_azienda['inps']}")
st.sidebar.markdown(f"**POS. INAIL:** {dati_azienda['inail']}")

# ------------------------------------------------------------------------------
# SELEZIONE CATEGORIA E DOCUMENTO
# ------------------------------------------------------------------------------
col_cat, col_doc = st.columns(2)

with col_cat:
    categoria_scelta = st.selectbox("Seleziona la Categoria Contrattuale:", list(DOCUMENTI_PER_CATEGORIA.keys()))

# Filtra opzioni in base all'azienda (es. Opera Intellettuale abilitata solo per HQE)
opzioni_doc = DOCUMENTI_PER_CATEGORIA[categoria_scelta].copy()
if azienda_scelta != "HQ Engineering S.r.l." and "Contratto d'Opera Intellettuale (P.IVA / Professionista - solo HQE)" in opzioni_doc:
    opzioni_doc.remove("Contratto d'Opera Intellettuale (P.IVA / Professionista - solo HQE)")

with col_doc:
    documento_scelto = st.selectbox("Seleziona il Tipo di Documento da Generare:", opzioni_doc)

st.divider()

# ------------------------------------------------------------------------------
# FORM DINAMICO DI INPUT
# ------------------------------------------------------------------------------
st.subheader("2. Dati del Lavoratore e Condizioni Contrattuali")

with st.form("form_dati_contratto"):
    st.markdown("#### 👤 Dati Anagrafici Lavoratore / Collaboratore")
    c1, c2, c3 = st.columns(3)
    with c1:
        nome = st.text_input("Nome*", placeholder="es. Roberto")
        luogo_nascita = st.text_input("Luogo di Nascita*", placeholder="es. Milano (MI)")
    with c2:
        cognome = st.text_input("Cognome*", placeholder="es. Baggio")
        data_nascita = st.date_input("Data di Nascita*", datetime.date(1990, 1, 1))
    with c3:
        codice_fiscale = st.text_input("Codice Fiscale*", placeholder="16 caratteri alfanumerici").upper()
        residenza = st.text_input("Indirizzo di Residenza*", placeholder="es. Via Roma 10, Milano")

    st.markdown("#### ⚙️ Condizioni Operative e Inquadramento")
    c4, c5, c6 = st.columns(3)
    with c4:
        mansione = st.text_input("Mansione / Incarico*", placeholder="es. Tecnico Installatore / Progettista CAD")
        sede_lavoro = st.text_input("Sede di Lavoro*", value="Milano")
    with c5:
        livello_ccnl = st.text_input("Livello Inquadramento CCNL", value="C2" if azienda_scelta == "QTECH S.r.l." else "3° Livello")
        ccnl_applicato = st.text_input("CCNL Applicato*", value=dati_azienda["ccnl_default"])
    with c6:
        orario_lavoro = st.text_input("Orario di Lavoro", value="Full Time (40 ore settimanali)")
        periodo_prova = st.text_input("Periodo di Prova", value="Come previsto da CCNL")

    st.markdown("#### 📅 Date e Scadenze")
    d1, d2, d3 = st.columns(3)
    with d1:
        data_documento = st.date_input("Data del Documento*", datetime.date.today())
        data_inizio = st.date_input("Data Inizio Rapporto / Decorrenza*", datetime.date.today())
    with d2:
        data_fine = st.date_input("Data Scadenza (se Temp. Det. / Co.Co.Co.)", datetime.date.today() + datetime.timedelta(days=365))
        data_stipula_originale = st.date_input("Data Stipula Contratto Originario (per Proroghe)", datetime.date.today() - datetime.timedelta(days=180))
    with d3:
        durata_minima_mesi = st.number_input("Mesi Stabilità Minima (Patto Stabilità)", min_value=6, max_value=60, value=24)

    st.markdown("#### 💶 Condizioni Economiche")
    e1, e2, e3 = st.columns(3)
    with e1:
        ral_lorda = st.number_input("Retribuzione Lorda Annua (RAL €)", min_value=0.0, step=1000.0, value=25000.0)
        compenso_netto_mese = st.number_input("Compenso Netto Mensile (Co.Co.Co. €)", min_value=0.0, step=100.0, value=1200.0)
    with e2:
        superminimo = st.number_input("Superminimo Assorbibile (€)", min_value=0.0, step=50.0, value=0.0)
        diaria_giornaliera = st.number_input("Diaria / Ticket Giornaliero (€/gg)", min_value=0.0, step=5.0, value=0.0)
    with e3:
        corrispettivo_stabilita = st.number_input("Corrispettivo Annuo Patto Stabilità (€)", min_value=0.0, step=100.0, value=0.0)
        penale_recesso_stabilita = st.number_input("Penale Recesso Anticipato Stabilità (€)", min_value=0.0, step=500.0, value=2000.0)

    st.markdown("#### 🚩 Clausole Opzionali e Checkbox")
    cl1, cl2 = st.columns(2)
    with cl1:
        clausola_fedelta = st.checkbox("Inserisci Obbligo di Fedeltà (art. 2105 c.c.)", value=True)
        clausola_trattenuta_dpi = st.checkbox("Inserisci Trattenuta DPI in caso di recesso in prova", value=True)
    with cl2:
        clausola_penale_rinuncia = st.checkbox("Inserisci Penale per mancata assunzione/rinuncia (10% RAL)", value=True)
        allegato_dlgs_104 = st.checkbox("Inserisci Allegato Informativo D.Lgs. 104/2022 (Trasparenza)", value=True)

    st.markdown("---")
    btn_genera = st.form_submit_button("🚀 Genera Documento Word (.docx)")

# ------------------------------------------------------------------------------
# ESECUZIONE DELLA GENERAZIONE DOCUMENTI
# ------------------------------------------------------------------------------
if btn_genera:
    if not nome or not cognome or not codice_fiscale:
        st.error("⚠️ Attenzione: Nome, Cognome e Codice Fiscale sono campi obbligatori!")
    else:
        # Prepara il dizionario del contesto Jinja2
        context = {
            "SOCIETA_NOME": dati_azienda["ragione_sociale"],
            "SOCIETA_CF_PIVA": dati_azienda["piva_cf"],
            "SOCIETA_INDIRIZZO": dati_azienda["indirizzo"],
            "SOCIETA_TEL": dati_azienda["telefono"],
            "SOCIETA_FAX": dati_azienda["fax"],
            "POSIZIONE_INPS": dati_azienda["inps"],
            "POSIZIONE_INAIL": dati_azienda["inail"],
            "CODICE_CNEL": dati_azienda["codice_cnel"],
            
            "NOME": nome.strip().capitalize(),
            "COGNOME": cognome.strip().upper(),
            "NOME_COMPLETO": f"{nome.strip().capitalize()} {cognome.strip().upper()}",
            "LUOGO_NASCITA": luogo_nascita.strip(),
            "DATA_NASCITA": data_nascita.strftime("%d/%m/%Y"),
            "CODICE_FISCALE": codice_fiscale.strip(),
            "RESIDENZA": residenza.strip(),
            
            "MANSIONE": mansione.strip(),
            "SEDE_LAVORO": sede_lavoro.strip(),
            "LIVELLO": livello_ccnl.strip(),
            "CCNL": ccnl_applicato.strip(),
            "ORARIO_LAVORO": orario_lavoro.strip(),
            "PERIODO_PROVA": periodo_prova.strip(),
            
            "DATA_DOCUMENTO": data_documento.strftime("%d/%m/%Y"),
            "DATA_INIZIO": data_inizio.strftime("%d/%m/%Y"),
            "DATA_FINE": data_fine.strftime("%d/%m/%Y"),
            "DATA_STIPULA_ORIGINALE": data_stipula_originale.strftime("%d/%m/%Y"),
            "DURATA_MINIMA_MESI": durata_minima_mesi,
            
            "RAL": f"{ral_lorda:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "COMPENSO_NETTO_MESE": f"{compenso_netto_mese:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "SUPERMINIMO": f"{superminimo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "DIARIA": f"{diaria_giornaliera:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "CORRISPETTIVO_STABILITA": f"{corrispettivo_stabilita:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "PENALE_STABILITA": f"{penale_recesso_stabilita:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            
            "CLAUSOLA_FEDELTA": clausola_fedelta,
            "CLAUSOLA_TRATTENUTA_DPI": clausola_trattenuta_dpi,
            "CLAUSOLA_PENALE_RINUNCIA": clausola_penale_rinuncia,
            "ALLEGATO_DLGS_104": allegato_dlgs_104
        }

        # Recupera il template Word corrispondente
        template_filename = TEMPLATE_MAP.get(documento_scelto)
        template_path = os.path.join("templates", template_filename) if template_filename else None

        if template_path and os.path.exists(template_path):
            try:
                # Caricamento ed elaborazione con docxtpl
                doc = DocxTemplate(template_path)
                doc.render(context)

                # Salvataggio in memoria
                file_stream = io.BytesIO()
                doc.save(file_stream)
                file_stream.seek(0)

                # Costruzione Naming Convention
                sigla_azienda = "HQE" if "HQ" in azienda_scelta else "QTECH"
                nome_doc_clean = documento_scelto.split("(")[0].strip().replace(" ", "_").upper()
                data_str = data_documento.strftime("%Y%m%d")
                out_filename = f"{nome_doc_clean}_{cognome.strip().upper()}_{nome.strip().upper()}_{sigla_azienda}_{data_str}.docx"

                st.success("✅ Documento generato con successo!")
                
                # Pulsante per il download del file Word
                st.download_button(
                    label="📥 Scarica File Word (.docx)",
                    data=file_stream,
                    file_name=out_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            except Exception as e:
                st.error(f"❌ Si è verificato un errore durante la generazione del documento: {e}")
        else:
            st.warning(f"⚠️ Modello Word non trovato nella cartella `templates/` ({template_filename}). Assicurarsi che il file `.docx` sia stato inserito correttamente.")
