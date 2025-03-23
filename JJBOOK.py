import streamlit as st
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

# -------------------- CONFIGURAÇÕES --------------------
st.set_page_config(page_title="JJBOOK 📚🤖", layout="wide")

API_SOURCES = {
    "archive": "https://archive.org/advancedsearch.php?q={query}+AND+mediatype%3Atexts&fl[]=identifier,title,description,creator,year,mediatype,format&output=json&rows=10&page=1",
    "scielo": "https://search.scielo.org/?q={query}&lang=pt&count=10&from=0&output=rss",
    "dominio": "http://www.dominiopublico.gov.br/pesquisa/PesquisaObraForm.do"
}

EXCLUDED_TERMS = ["zlibrary", "livropedia", "indicalivros", "amazon", "notícia", "bdjur"]

ALLOWED_TERMS = ["tese", "dissertação", "monografia", "livro", "artigo", "acadêmico", "científico"]

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
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 20px;
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

st.write("🔎 Pesquise livros acadêmicos, teses e dissertações completas abaixo:")

# -------------------- FUNÇÃO PARA FILTRAGEM FUZZY --------------------
def is_relevant(title, description):
    combined = f"{title.lower()} {description.lower()}"
    relevance_score = max([fuzz.partial_ratio(term, combined) for term in ALLOWED_TERMS])
    exclusion_score = max([fuzz.partial_ratio(term, combined) for term in EXCLUDED_TERMS])
    return relevance_score > 50 and exclusion_score < 30

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
            if is_relevant(title, desc):
                results.append({
                    "title": title,
                    "description": desc,
                    "link": f"https://archive.org/details/{doc.get('identifier')}",
                    "image": "https://archive.org/services/img/" + doc.get("identifier", "")
                })
    return results

# -------------------- BUSCA NO DOMÍNIO PÚBLICO --------------------
def search_dominio(query):
    payload = {"busca_titulo": query, "select_midia": "0"}
    resp = requests.post(API_SOURCES["dominio"], data=payload)
    results = []
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")
        obras = soup.find_all("tr", {"class": "fundoPadraoLista"})
        for obra in obras:
            cols = obra.find_all("td")
            if len(cols) > 1:
                title = cols[0].get_text(strip=True)
                desc = "Obra disponível no Domínio Público"
                if is_relevant(title, desc):
                    results.append({
                        "title": title,
                        "description": desc,
                        "link": "http://www.dominiopublico.gov.br" + cols[0].find("a")["href"],
                        "image": "https://via.placeholder.com/150"
                    })
    return results

# -------------------- INTERFACE --------------------
query = st.text_input("Digite a palavra-chave:", "")

if query:
    st.info("⏳ Buscando resultados relevantes...")

    archive_results = search_archive(query)
    dominio_results = search_dominio(query)

    all_results = archive_results + dominio_results

    if not all_results:
        st.warning("Nenhum resultado acadêmico encontrado.")
    else:
        st.subheader("📚 Resultados filtrados e relevantes:")
        cols = st.columns(2)

        for idx, result in enumerate(all_results[:5]):
            with cols[idx % 2]:
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                st.image(result["image"], width=150)
                st.markdown(f"### [{result['title']}]({result['link']})")
                st.markdown(f"📝 {result['description']}")
                st.markdown(f"📄 [Download ou Acessar]({result['link']})")
                st.markdown(f"</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("Desenvolvido por JJ I.A.")
