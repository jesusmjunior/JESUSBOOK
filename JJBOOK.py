import streamlit as st
import requests

# --- CONFIGURAÇÕES DA SUA API ---
API_KEY = "AIzaSyAKibc0A3TerDdfQeZBLePxU01PbK_53Lw"
CX_ID = "YOUR_CX_ID"  # Substitua pelo seu ID do mecanismo Google

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Buscador Visual de PDFs", layout="wide")
st.title("📚 Estante Visual - Buscador de PDFs")

# --- INPUT DO USUÁRIO ---
query = st.text_input("🔎 Digite o tema ou palavra-chave para buscar:", "")

if query:
    # --- CHAMADA À GOOGLE API ---
    params = {
        "key": API_KEY,
        "cx": CX_ID,
        "q": f"{query} filetype:pdf"
    }
    response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)

    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])

        if not items:
            st.warning("Nenhum resultado encontrado!")
        else:
            st.subheader(f"📄 Resultados para: **{query}**")

            # --- ORGANIZAÇÃO DOS CARDS ---
            cols = st.columns(2)  # 2 cards por linha

            for idx, item in enumerate(items[:10]):  # Limite de 10 resultados
                title = item.get("title")
                link = item.get("link")
                snippet = item.get("snippet", "")
                image = item.get("pagemap", {}).get("cse_thumbnail", [{}])[0].get("src", "https://via.placeholder.com/150")

                with cols[idx % 2]:
                    st.image(image, width=150)
                    st.markdown(f"### [{title}]({link})")
                    st.markdown(f"📝 {snippet}")
                    st.markdown(f"📄 [Download PDF]({link})", unsafe_allow_html=True)
                    st.markdown("---")

            st.markdown(f"🔗 [Buscar mais resultados no Google](https://www.google.com/search?q={query}+filetype:pdf)")

    else:
        st.error("Erro ao consultar a API do Google.")
