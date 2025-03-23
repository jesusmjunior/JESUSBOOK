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
@keyframes float {
  0% {transform: translateY(0px);}
  50% {transform: translateY(-20px);}
  100% {transform: translateY(0px);}
}
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
  width: 80px;
  height: 80px;
}
.robot-label {
  background-color: #00C4FF;
  color: white;
  padding: 5px 10px;
  border-radius: 8px;
  margin-top: 5px;
  font-weight: bold;
}
h1 {
  text-align: center;
  color: #FF4B4B;
  font-size: 48px;
}
.card {
  background-color: #f0f8ff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 4px 4px 12px rgba(0,0,0,0.1);
  margin-bottom: 25px;
  transition: 0.3s;
}
.card:hover {
  transform: scale(1.03);
  box-shadow: 6px 6px 15px rgba(0,0,0,0.2);
}
.card-title {
  color: #1a237e;
  font-weight: bold;
}
.card-description {
  color: #424242;
}
.download-link {
  background-color: #00C4FF;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
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

st.write("🔎 Cole abaixo um trecho ou tema para rastrear e encontre materiais organizados por tipo, assunto e preferências:")

# -------------------- FUNÇÃO DE PARSER LÓGICO --------------------
def parse_query(query):
    key_info = {
        "document_type": [],
        "subject": [],
        "year_start": 2010,
        "year_end": 2025,
        "priority": []
    }
    document_types = ["tese", "dissertação", "monografia", "livro", "artigo"]
    subjects = ["direito", "constitucional", "lei", "python", "llm", "robô"]

    for word in query.lower().split():
        if word in document_types:
            key_info["document_type"].append(word)
        elif word in subjects:
            key_info["subject"].append(word)
        elif re.match(r"\\d{4}", word):
            year = int(word)
            if year < 2025 and year > 1900:
                if not key_info["year_start"]:
                    key_info["year_start"] = year
                else:
                    key_info["year_end"] = year

    if not key_info["document_type"]:
        key_info["document_type"] = ["livro", "tese", "artigo"]
    if not key_info["subject"]:
        key_info["subject"] = ["acadêmico", "científico"]

    return key_info

# -------------------- FUNÇÃO DE DECODIFICAÇÃO LÓGICA --------------------
def advanced_logic(result, query_info):
    score = 0
    title = result.get("title", "").lower()
    desc = result.get("description", "").lower()
    year = result.get("year", "")

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
            desc = doc.get("description", "") or "Livro/Texto disponível no Archive.org"
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
query = st.text_area("Cole aqui o trecho para rastrear informações:", "")

# -------------------- RESULTADOS --------------------
if query:
    st.info("⏳ Processando informações e aplicando lógica fuzzy...")
    parsed_query = parse_query(query)

    archive_results = search_archive(query, parsed_query)

    if not archive_results:
        st.warning("Nenhum resultado encontrado.")
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
