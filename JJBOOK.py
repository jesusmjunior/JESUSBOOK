import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="JJBOOK 📚🤖", layout="wide")

# --- CSS PERSONALIZADO ---
custom_css = """
<style>
@keyframes slide {
  0% {top: -100px; opacity: 0;}
  50% {opacity: 1;}
  100% {top: 100%; opacity: 0;}
}
.robot {
  position: fixed;
  left: 10px;
  font-size: 24px;
  animation: slide 5s infinite;
  color: #00C4FF;
}
h1 {
  text-align: center;
  color: #FF4B4B;
  font-size: 48px;
}
</style>
<div class="robot">🤖 JJ I.A.</div>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("# JJBOOK 📚🤖")

# --- DESCRIÇÃO ---
st.write("🔎 Pesquise abaixo livros, teses, dissertações e monografias completas!")

# --- EMBED GOOGLE CSE ---
cse_html = """
<script async src="https://cse.google.com/cse.js?cx=706995a2060d64dcc"></script>
<div class="gcse-search"></div>
"""
st.components.v1.html(cse_html, height=800, scrolling=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("Desenvolvido por JJ I.A.")
