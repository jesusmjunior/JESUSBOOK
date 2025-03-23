import streamlit as st
import requests

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

st.write("🔎 Pesquise livros acadêmicos completos abaixo:")

# -------------------- LÓGICA DE REFINAMENTO --------------------
def logic_engine(result):
    score = 0
    title = result.get("title", "").lower()
    desc = result.get("description", "").lower()
    if any(term in title for term in ["tese", "dissertação", "monografia", "livro", "acadêmico", "científico"]):
        score += 2
    if "pdf" in desc:
        score += 1
    if len(desc) > 100:
        score += 1
    return score >= 2  # Ajuste de critério para exibir ou não

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
            if logic_engine(result_data):
                results.append(result_data)
    return results

# -------------------- INTERFACE --------------------
query = st.text_input("Digite a palavra-chave:", "")

if query:
    st.info("⏳ Buscando resultados relevantes com refinamento...")

    archive_results = search_archive(query)

    if not archive_results:
        st.warning("Nenhum resultado acadêmico encontrado.")
    else:
        st.subheader("📚 Resultados refinados e relevantes:")
        cols = st.columns(2)

        for idx, result in enumerate(archive_results[:5]):
            with cols[idx % 2]:
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                st.image(result["image"], width=150)
                st.markdown(f"<div class='card-title'>📘 {result['title']}</div>", unsafe_allow_html=True)
                st.markdown(f"👤 Autor: {result['author']}")
                st.markdown(f"📅 Ano: {result['year']}")
                st.markdown(f"<div class='card-description'>📝 {result['description']}</div>", unsafe_allow_html=True)
                st.markdown(f"<a class='download-link' href='{result['link']}' target='_blank'>📄 Download PDF</a>", unsafe_allow_html=True)
                st.markdown(f"</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("Desenvolvido por JJ I.A.")
