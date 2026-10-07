import streamlit as st
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
from core.utils import load_config
from core.renderers import Renderer


st.set_page_config(page_title="strategy-toolkit", layout="wide")

st.title("strategy-toolkit")
st.caption("YAML → Markdown/JSON/CSV (one-click bundle)")

renderer = Renderer()

with st.sidebar:
    st.subheader("Load config")
    uploaded = st.file_uploader("Upload YAML", type=["yaml", "yml"])
    text = st.text_area("Or paste YAML", height=200)
    st.subheader("Examples")
    ex_dir = Path(__file__).parent / "examples"
    examples = []
    for mod in ["issue_tree", "decision_matrix", "strategy_canvas"]:
        for p in (ex_dir / mod).glob("*.yaml"):
            examples.append((mod, p))
    example = st.selectbox("Load example", [("—", None)] + [(f"{m}/{p.name}", p) for m, p in examples])
    if example[1]:
        st.info(f"Loaded {example[1].name}")
        text = example[1].read_text()

cfg = None
error = None
if uploaded:
    try:
        text = uploaded.read().decode("utf-8", errors="ignore")
    except Exception as e:
        error = str(e)
if text:
    try:
        cfg = load_config(text)
    except Exception as e:
        error = str(e)

if error:
    st.error(error)

if cfg:
    st.subheader(f"Module: {cfg.module}")
    md = renderer.to_markdown(cfg)
    j = renderer.to_json(cfg)
    csv = renderer.to_csv(cfg)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Live Markdown Preview")
        st.markdown(md)
    with c2:
        st.markdown("### JSON / CSV (quick view)")
        st.code(j, language="json")
        st.code(csv, language="text")
    st.markdown("### Export (one-click bundle)")
    zip_buf = BytesIO()
    with ZipFile(zip_buf, "w") as z:
        z.writestr(f"{cfg.module}.md", md)
        z.writestr(f"{cfg.module}.json", j)
        z.writestr(f"{cfg.module}.csv", csv)
    zip_buf.seek(0)
    st.download_button(
        "Download md+json+csv.zip",
        data=zip_buf.getvalue(),
        file_name=f"{cfg.module}_bundle.zip",
        mime="application/zip",
    )
else:
    st.info("Paste YAML or upload a file to get started.")
