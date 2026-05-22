import streamlit as st
import pandas as pd

# 1. Configurazione della pagina web
st.set_page_config(
    page_title="Gestione Flotta Scaffali Biblioteca",
    page_icon="📚",
    layout="wide"
)

# 2. Inizializzazione dello stato della memoria (Session State)
if 'flotta_scaffali' not in st.session_state:
    # Struttura dati iniziale con due scaffali di esempio
    st.session_state.flotta_scaffali = {
        'Scaffale "Libri Storici"': {
            'ripiani': 4,
            'moduli': 3,
            'lunghezza_modulo': 2.0,
            'tara': 80.0,
            'matrice': {
                "3_0": ["Tipologia A (Enciclopedie)", 40.0],
                "3_1": ["Tipologia B (Riviste)", 25.0],
                "1_2": ["Tipologia E (Fascicoli)", 120.0],
                "0_1": ["Tipologia H (Archivio)", 300.0]
            }
        },
        'Scaffale "Narrativa Moderna"': {
            'ripiani': 3,
            'moduli': 4,
            'lunghezza_modulo': 1.5,
            'tara': 60.0,
            'matrice': {}
        }
    }

# Funzione di utilità per garantire che tutte le celle di uno scaffale esistano
def garantisci_matrice(nome_scaf):
    scaf = st.session_state.flotta_scaffali[nome_scaf]
    for r in range(scaf['ripiani']):
        for m in range(scaf['moduli']):
            chiave = f"{r}_{m}"
            if chiave not in scaf['matrice']:
                scaf['matrice'][chiave] = ["Vuoto", 0.0]

# Garantiamo la consistenza iniziale
for nome in st.session_state.flotta_scaffali:
    garantisci_matrice(nome)


# 3. BARRA LATERALE (Sidebar) - AGGIUNTA NUOVI SCAFFALI A PIACIMENTO
st.sidebar.header("➕ Aggiungi Nuovo Scaffale")
with st.sidebar.form("form_nuovo_scaffale", clear_on_submit=True):
    nuovo_nome = st.text_input("Nome univoco dello scaffale")
    nuovo_ripiani = st.number_input("Numero di Ripiani", min_value=1, max_value=20, value=4)
    nuovo_moduli = st.number_input("Numero di Moduli (Colonne)", min_value=1, max_value=15, value=3)
    nuova_lunghezza = st.number_input("Lunghezza modulo (m)", min_value=0.5, value=2.0, step=0.5)
    nuova_tara = st.number_input("Tara struttura (kg)", min_value=0.0, value=80.0, step=5.0)
    
    crea_scaffale = st.form_submit_button("Crea Scaffale")
    if crea_scaffale:
        if not nuovo_nome.strip():
            st.sidebar.error("Inserisci un nome valido!")
        elif nuovo_nome in st.session_state.flotta_scaffali:
            st.sidebar.error("Uno scaffale con questo nome esiste già!")
        else:
            st.session_state.flotta_scaffali[nuovo_nome] = {
                'ripiani': nuovo_ripiani,
                'moduli': nuovo_moduli,
                'lunghezza_modulo': nuova_lunghezza,
                'tara': nuova_tara,
                'matrice': {}
            }
            garantisci_matrice(nuovo_nome)
            st.sidebar.success(f"✓ '{nuovo_nome}' creato!")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🗑️ Elimina Scaffale")
scaffale_da_eliminare = st.sidebar.selectbox("Seleziona scaffale da rimuovere", ["---"] + list(st.session_state.flotta_scaffali.keys()))
if scaffale_da_eliminare != "---":
    if st.sidebar.button("Conferma Eliminazione", type="primary"):
        del st.session_state.flotta_scaffali[scaffale_da_eliminare]
        st.sidebar.success(f"Eliminato {scaffale_da_eliminare}")
        st.rerun()


# 4. CORPO PRINCIPALE
st.title("📚 Gestione Multi-Scaffale e Flotta Biblioteca")

# Selezione dello scaffale attivo da visualizzare/gestire
lista_scaffali = list(st.session_state.flotta_scaffali.keys())
if not lista_scaffali:
    st.info("Nessuno scaffale presente. Creane uno dalla barra laterale!")
else:
    scaffale_attivo = st.selectbox("📂 Seleziona lo Scaffale da gestire:", lista_scaffali)
    
    scaf_corrente = st.session_state.flotta_scaffali[scaffale_attivo]
    r_tot = scaf_corrente['ripiani']
    m_tot = scaf_corrente['moduli']
    
    st.write(f"Configurazione geometrica: **{r_tot} Ripiani** × **{m_tot} Moduli** | Lunghezza modulo: **{scaf_corrente['lunghezza_modulo']}m** | Tara: **{scaf_corrente['tara']} kg**")
    
    tab_mappa, tab_modifica = st.tabs(["👁️ Mappa & Report Pesi", "✏️ Modifica & Replica Avanzata"])
    
    with tab_mappa:
        # Generazione DataFrame per la visualizzazione invertita (ripiano alto in cima)
        righe_tabella = []
        for r in range(r_tot - 1, -1, -1):
            info_riga = {}
            for m in range(m_tot):
                tipologia, peso = scaf_corrente['matrice'][f"{r}_{m}"]
                info_riga[f"Modulo {m+1}"] = f"[{tipologia}] {peso} kg"
            righe_tabella.append(info_riga)
            
        indici_verticali = [f"Ripiano {i}" for i in range(r_tot, 0, -1)]
        df_visivo = pd.DataFrame(righe_tabella, index=indici_verticali)
        st.dataframe(df_visivo, use_container_width=True)
        
        # Calcolo dei pesi per lo scaffale corrente
        peso_merce_singolo = sum(scaf_corrente['matrice'][f"{r}_{m}"][1] for r in range(r_tot) for m in range(m_tot))
        peso_complessivo_singolo = peso_merce_singolo + scaf_corrente['tara']
        
        # Calcolo dei pesi globali (Flotta Intera)
        peso_merce_flotta = 0.0
        tara_flotta = 0.0
        for nome, s in st.session_state.flotta_scaffali.items():
            peso_merce_flotta += sum(s['matrice'][f"{r}_{m}"][1] for r in range(s['ripiani']) for m in range(s['moduli']))
            tara_flotta += s['tara']
        peso_complessivo_flotta = peso_merce_flotta + tara_flotta
        
        st.markdown("---")
        st.subheader("📊 Calcolo dei Pesi")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Questo Scaffale ({scaffale_attivo}):**")
            st.write(f"• Peso Merce: {peso_merce_singolo:,.1f} kg")
            st.write(f"• Peso Complessivo (con Tara): **{peso_complessivo_singolo:,.1f} kg**")
        with col2:
            st.markdown(f"**Flotta Totale ({len(lista_scaffali)} Scaffali attivi):**")
            st.write(f"• Peso Merce Totale Flotta: {peso_merce_flotta:,.1f} kg")
            st.markdown(f"<div style='background-color:#e2f0d9; padding:10px; border-radius:5px;'><b>PESO COMPLESSIVO FLOTTA: {peso_complessivo_flotta:,.1f} kg</b><br><small>Tara complessiva strutture: {tara_flotta} kg</small></div>", unsafe_allow_html=True)

    with tab_modifica:
        st.subheader("✏️ Editor e Strumenti di Copia tra Scaffali")
        
        col_sel_r, col_sel_m = st.columns(2)
        with col_sel_r:
            ripiano_scelto = st.selectbox("Seleziona Ripiano", list(range(1, r_tot + 1)), index=r_tot-1)
        with col_sel_m:
            modulo_scelto = st.selectbox("Seleziona Modulo", list(range(1, m_tot + 1)))
            
        r_idx = ripiano_scelto - 1
        m_idx = modulo_scelto - 1
        chiave_corrente = f"{r_idx}_{m_idx}"
        
        tipo_att, peso_att = scaf_corrente['matrice'][chiave_corrente]
        
        st.markdown(f"Modifica punto: **Ripiano {ripiano_scelto}**, **Modulo {modulo_scelto}** di *{scaffale_attivo}*")
        
        with st.form("form_super_modifica"):
            nuovo_tipo = st.text_input("Tipologia materiale / Libri", value=tipo_att)
            nuovo_peso = st.number_input("Peso livello (kg)", min_value=0.0, value=float(peso_att), step=5.0)
            
            st.markdown("---")
            st.markdown("🔄 **Opzioni di Replica e Copia Esterna:**")
            
            # Opzione 1: Replica locale
            rep_colonna = st.checkbox("Applica a TUTTI i ripiani di questo modulo (in questo scaffale)")
            rep_scaffale = st.checkbox("Rendi l'INTERO scaffale corrente uniforme con questi dati")
            
            # Opzione 2: COPIA SU ALTRI SCAFFALI (Stessa coordinata o intero scaffale)
            st.markdown("**Copia verso altri scaffali della biblioteca:**")
            scaffali_destinazione = st.multiselect(
                "Seleziona uno o più scaffali di destinazione:",
                [n for n in lista_scaffali if n != scaffale_attivo]
            )
            
            st.markdown("<small>Nota: La copia sulla stessa cella avverrà solo se lo scaffale di destinazione possiede fisicamente quel ripiano e quel modulo.</small>", unsafe_allow_html=True)
            copia_stessa_cella = st.checkbox("Copia sulla STESSA COORDINATA (Ripiano/Modulo) degli scaffali selezionati")
            copia_tutto_scaffale_dest = st.checkbox("RIEMPI INTERAMENTE gli scaffali selezionati con questo materiale")
            
            pulsante_salva = st.form_submit_form_button if hasattr(st, "form_submit_form_button") else st.form_submit_button("Salva ed Esegui Repliche")
            
            if pulsante_salva:
                # 1. Salva la cella di partenza
                scaf_corrente['matrice'][chiave_corrente] = [nuovo_tipo, nuovo_peso]
                
                # 2. Repliche all'interno dello stesso scaffale
                if rep_colonna:
                    for r in range(r_tot):
                        scaf_corrente['matrice'][f"{r}_{m_idx}"] = [nuovo_tipo, nuovo_peso]
                if rep_scaffale:
                    for r in range(r_tot):
                        for m in range(m_tot):
                            scaf_corrente['matrice'][f"{r}_{m}"] = [nuovo_tipo, nuovo_peso]
                            
                # 3. Repliche verso ALTRI scaffali della biblioteca
                if scaffali_destinazione:
                    for s_dest_nome in scaffali_destinazione:
                        s_dest = st.session_state.flotta_scaffali[s_dest_nome]
                        
                        # Copia mirata sulla stessa coordinata ripiano/modulo
                        if copia_stessa_cella:
                            # Verifichiamo prima che lo scaffale di destinazione sia abbastanza grande
                            if r_idx < s_dest['ripiani'] and m_idx < s_dest['moduli']:
