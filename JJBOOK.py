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

st.write("🔎 Cole abaixo um trecho do texto que deseja rastrear e encontrar materiais relacionados:")

# -------------------- PARSER LÓGICO SIMPLES --------------------
def parse_query(query):
    weights = {"tese": 3, "dissertação": 3, "monografia": 2, "livro": 2, "artigo": 2, "acadêmico": 1, "científico": 1, "python": 2, "llm": 2, "direito": 2, "constitucional": 2, "lei": 2}
    parsed = {}
    for key, weight in weights.items():
        if re.search(rf"\b{key}\b", query.lower()):
            parsed[key] = weight
    return parsed

# -------------------- MOTOR LÓGICO ALFA/BETA/GAMA + SEMÂNTICA --------------------
def advanced_logic(result, query):
    score = 0
    title = result.get("title", "").lower()
    desc = result.get("description", "").lower()
    year = result.get("year", "")

    key_terms = {"alfa": ["tese", "dissertação"], "beta": ["monografia", "livro"], "gama": ["artigo", "acadêmico", "científico", "llm", "python"]}
    query_terms = parse_query(query)

    for level, terms in key_terms.items():
        for term in terms:
            if term in title or term in desc or term in query_terms:
                score += {"alfa": 3, "beta": 2, "gama": 1}[level]

    for term, weight in query_terms.items():
        if term in title or term in desc:
            score += weight

    if len(desc) > 100:
        score += 1

    try:
        if int(year) >= 2018:
            score += 2
    except:
        pass

    return score >= 5

# -------------------- BUSCA NO ARCHIVE --------------------
def search_archive(query):
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
            if advanced_logic(result_data, query):
                results.append(result_data)
    return results

# -------------------- INPUT DE TEXTO PARA RASTREAMENTO --------------------
query = st.text_area("Cole aqui o trecho ou tema para rastreamento:", "")

# -------------------- RESULTADOS --------------------
if query:
    st.info("⏳ Buscando resultados refinados com lógica avançada...")

    archive_results = search_archive(query)

    if not archive_results:
        st.warning("Nenhum resultado acadêmico encontrado.")
    else:
        st.subheader("📚 Resultados relevantes e refinados:")
        cols = st.columns(2)

        for idx, result in enumerate(archive_results[:5]):
            bullets = [
                f"📕 **Título:** {result['title']}",
                f"👤 **Autor:** {result.get('author', 'Desconhecido')}",
                f"📅 **Ano:** {result.get('year', 'N/A')}",
                f"📄 [Baixar PDF]({result['link']})",
                f"✨ {result['description'][:150]}..."
            ]
            with cols[idx % 2]:
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                st.image(result.get("image", "https://via.placeholder.com/150"), width=150)
                st.markdown("\n".join(bullets))
                st.markdown(f"</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("Desenvolvido por JJ I.A. 🤖")
