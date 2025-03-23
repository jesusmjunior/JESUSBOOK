import streamlit as st
import requests
import json
import re

# -------------------- CONFIGURAÇÕES --------------------
st.set_page_config(page_title="JJBOOK 📚🤖", layout="wide")

# Lista de bases confiáveis diretamente no código
trusted_sources = [
    "archive.org",
    "bibliotecadigital.tse.jus.br",
    "books.scielo.org",
    "dominiopublico.gov.br",
    "capes.gov.br",
    "bdtd.ibict.br",
    "repositorio.unesp.br",
    "repositorio.ufsc.br",
    "repositorio.unb.br",
    "repositorio.ufmg.br",
    "www.scielo.org",
    "www.periodicos.capes.gov.br",
    "www.scholar.google.com.br",
    "www.redalyc.org",
    "www.bdtd.ibict.br",
    "www.doaj.org",
    "www.pubmed.ncbi.nlm.nih.gov",
    "www.eric.ed.gov",
    "www.lilacs.bvsalud.org",
    "www.scifinder.cas.org",
    "www.scopus.com",
    "www.webofscience.com",
    "www.jstor.org",
    "www.sciencedirect.com",
    "www.link.springer.com",
    "www.ieeexplore.ieee.org",
    "www.apa.org",
    "www.embase.com",
    "www.openalex.org",
    "www.openedition.org",
    "www.latindex.org",
    "www.oaister.worldcat.org",
    "www.base-search.net",
    "www.v2.sherpa.ac.uk",
    "www.openaire.eu",
    "www.ncbi.nlm.nih.gov",
    "www.arxiv.org"
]

API_SOURCES = {
    "archive": "https://archive.org/advancedsearch.php?q={query}+AND+mediatype%3Atexts&fl[]=identifier,title,description,creator,year,mediatype,format&output=json&rows=10&page=1"
}

# -------------------- CSS PERSONALIZADO --------------------
custom_css = """
<style>
.robot-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: float 3s infinite;
}
.robot-container img {
  width: 60px;
  height: 60px;
}
.robot-label {
  background-color: #00C4FF;
  color: white;
  padding: 4px 8px;
  border-radius: 8px;
  margin-top: 4px;
  font-weight: bold;
}
h1 {
  text-align: center;
  color: #FF4B4B;
  font-size: 42px;
}
.card {
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 10px;
  box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}
.card-title {
  color: #1a237e;
  font-weight: bold;
}
.card-description {
  color: #424242;
  font-size: 14px;
}
.download-link {
  background-color: #00C4FF;
  color: white;
  padding: 6px 10px;
  border-radius: 6px;
  text-decoration: none;
}
</style>
<div class="robot-container">
  <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" alt="JJ I.A. Robot">
  <div class="robot-label">🤖 JJ I.A.</div>
</div>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# -------------------- CABEÇALHO --------------------
st.markdown("# JJBOOK 📚🤖")
st.write("🔎 Preencha os campos abaixo para rastrear materiais por tipo, assunto e preferências.")

# -------------------- INPUTS SEPARADOS --------------------
with st.form("search_form"):
    target = st.text_input("🎯 Defina seu tema ou target principal:")
    doc_type = st.multiselect("📄 Tipo de Documento:", ["Tese", "Dissertação", "Monografia", "Livro", "Artigo"], default=["Tese", "Artigo"])
    year_range = st.slider("📅 Ano de publicação:", 2005, 2025, (2015, 2025))
    submitted = st.form_submit_button("🔍 Buscar")

# -------------------- FUNÇÃO DE PARSER --------------------
def parse_query(target, doc_type, year_range):
    key_info = {
        "document_type": [x.lower() for x in doc_type],
        "subject": [],
        "year_start": year_range[0],
        "year_end": year_range[1]
    }
    subjects = ["direito", "constitucional", "lei", "python", "llm", "robô", "chatbot"]

    for word in target.lower().split():
        if word in subjects:
            key_info["subject"].append(word)

    if not key_info["subject"]:
        key_info["subject"] = ["acadêmico", "científico"]

    return key_info

# -------------------- MOTOR LÓGICO --------------------
def advanced_logic(result, query_info):
    score = 0
    title = str(result.get("title", "")).lower()
    desc = str(result.get("description", "")).lower()
    year = str(result.get("year", ""))

    for doc_type in query_info["document_type"]:
        if doc_type in title or doc_type in desc:
            score += 3

    for subj in query_info["subject"]:
        if subj in title or subj in desc:
            score += 2

    try:
        if int(year) >= query_info["year_start"] and int(year) <= query_info["year_end"]:
            score += 2
    except:
        pass

    if len(desc) > 100:
        score += 1

    return score >= 5

# -------------------- BUSCA NO ARCHIVE + BASES CONFIÁVEIS --------------------
def search_archive(query, parsed_query):
    url = API_SOURCES["archive"].format(query=query)
    resp = requests.get(url)
    results = []
    if resp.status_code == 200:
        data = resp.json()
        for doc in data.get("response", {}).get("docs", []):
            title = doc.get("title", "")
            desc = doc.get("description", "") or "Livro disponível no Archive.org"
            author = doc.get("creator", "Autor desconhecido")
            year = doc.get("year", "Ano não informado")
            source = doc.get("identifier", "")
            
            # Apenas incluir se for base confiável
            if any(base in source for base in trusted_sources):
                result_data = {
                    "title": title,
                    "description": desc,
                    "author": author,
                    "year": year,
                    "link": f"https://archive.org/details/{source}",
                    "image": "https://archive.org/services/img/" + source
                }
                if advanced_logic(result_data, parsed_query):
                    results.append(result_data)
    return results

# -------------------- RESULTADOS --------------------
if submitted and target:
    st.info("⏳ Buscando resultados com lógica refinada...")
    parsed_query = parse_query(target, doc_type, year_range)
    archive_results = search_archive(target, parsed_query)

    if not archive_results:
        st.warning("Nenhum resultado encontrado. Tente redefinir as palavras-chave.")
    else:
        st.subheader("📚 Resultados organizados:")
        cols = st.columns(2)

        for idx, result in enumerate(archive_results[:10]):
            bullets = [
                f"📕 **Título:** {result['title']}",
                f"👤 **Autor:** {result.get('author', 'Desconhecido')}",
                f"🏫 **Publicação:** {result.get('year', 'N/A')}",
                f"📄 [Baixar PDF]({result['link']})",
                f"🌐 [Site Original]({result['link']})",
                f"✨ {result['description'][:150]}..."
            ]
            with cols[idx % 2]:
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                st.image(result.get("image", "https://via.placeholder.com/150"), width=120)
                st.markdown("\n".join(bullets))
                st.markdown(f"</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("Desenvolvido por JJ I.A. 🤖")

# -------------------- LIMPA CACHE --------------------
st.cache_data.clear()
