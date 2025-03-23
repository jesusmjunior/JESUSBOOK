import streamlit as st
import requests
import json
import re

# -------------------- CONFIGURAÇÕES --------------------
st.set_page_config(page_title="JJBOOK 📚🤖", layout="wide")

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
st.write("🔎 Cole abaixo um trecho ou tema para rastrear materiais por tipo, assunto e preferências.")

# -------------------- FUNÇÃO DE PARSER --------------------
def parse_query(query):
    key_info = {
        "document_type": [],
        "subject": [],
        "year_start": 2010,
        "year_end": 2025
    }
    document_types = ["tese", "dissertação", "monografia", "livro", "artigo"]
    subjects = ["direito", "constitucional", "lei", "python", "llm", "robô"]

    for word in query.lower().split():
        if word in document_types:
            key_info["document_type"].append(word)
        elif word in subjects:
            key_info["subject"].append(word)
        elif re.match(r"\d{4}", word):
            year = int(word)
            if 1900 < year < 2025:
                if key_info["year_start"] == 2010:
                    key_info["year_start"] = year
                else:
                    key_info["year_end"] = year

    if not key_info["document_type"]:
        key_info["document_type"] = ["livro", "tese", "artigo"]
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

# -------------------- BUSCA NO ARCHIVE --------------------
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
            result_data = {
                "title": title,
                "description": desc,
                "author": author,
                "year": year,
                "link": f"https://archive.org/details/{doc.get('identifier')}",
                "image": "https://archive.org/services/img/" + doc.get("identifier", "")
            }
            if advanced_logic(result_data, parsed_query):
                results.append(result_data)
    return results

# -------------------- INPUT DE TEXTO --------------------
with st.form("search_form"):
    query = st.text_area("✏️ Cole seu tema ou trecho para rastrear informações:", "", height=100)
    submitted = st.form_submit_button("🔍 Buscar")

# -------------------- RESULTADOS --------------------
if submitted and query:
    st.info("⏳ Buscando e aplicando lógica fuzzy...")
    parsed_query = parse_query(query)
    archive_results = search_archive(query, parsed_query)

    if not archive_results:
        st.warning("Nenhum resultado encontrado. Tente modificar ou ampliar seu texto.")
    else:
        st.subheader("📚 Resultados organizados:")
        cols = st.columns(2)

        for idx, result in enumerate(archive_results[:10]):
            bullets = [
                f"📕 **Título:** {result['title']}",
                f"👤 **Autor:** {result.get('author', 'Desconhecido')}",
                f"📅 **Ano:** {result.get('year', 'N/A')}",
                f"📄 [Baixar PDF]({result['link']})",
                f"🌐 [Acessar Site Original]({result['link']})",
                f"✨ {result['description'][:150]}..."
            ]
            with cols[idx % 2]:
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                st.image(result.get("image", "https://via.placeholder.com/150"), width=120)
                st.markdown("\n".join(bullets))
                st.markdown(f"</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("Desenvolvido por JJ I.A. 🤖")

# -------------------- LIMPA CACHE (Simples) --------------------
st.cache_data.clear()
