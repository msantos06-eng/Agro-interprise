import requests
with st.sidebar:


    link = r.json()["url"]

    st.sidebar.markdown(f"[👉 Pagar agora]({link})")
    st.image("https://img.icons8.com/color/96/corn.png", width=56)
    st.title("AgroForce")
    st.caption("Agricultura de Precisão")
    st.divider()
    
    if plano == "free":
    st.sidebar.warning("Plano FREE (3 talhões / 15 dias)")

    if st.sidebar.button("Upgrade"):
        r = requests.get(f"{API}/create-payment", headers=headers)
        link = r.json()["url"]
        st.sidebar.markdown(f"[👉 Pagar agora]({link})")


    if st.session_state.talhoes:
        st.subheader(f"Talhões ({len(st.session_state.talhoes)})")
        for i, t in enumerate(st.session_state.talhoes):
            ativo = i == st.session_state.idx_ativo
            label = f"{'▶️ ' if ativo else ''}{t['nome']}  --  {t['stats']['area_ha']} ha"
            if st.button(label, key=f"sel_{i}", use_container_width=True,
                         type="primary" if ativo else "secondary"):
                st.session_state.idx_ativo = i
                st.rerun()

        st.divider()
        ta = talhao_ativo()
        if ta:
            st.caption("**Talhão ativo:**")
            st.metric("Área", f"{ta['stats']['area_ha']} ha")
            st.metric("Perímetro", f"{ta['stats']['perimeter_m']} m")
            for lbl, key in [("Grade NDVI", "grid_cells"), ("VRA", "vra_cells"),
                              ("Linhas", "lines"), ("Buffer", "buffer_geom")]:
                val = ta.get(key)
                if val is not None:
                    n = len(val) if isinstance(val, list) else 1
                    st.success(f"✅ {lbl} ({n})")
                else:
                    st.caption(f"⬜ {lbl}")

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🗑️ Remover ativo", use_container_width=True):
                idx = st.session_state.idx_ativo
                st.session_state.talhoes.pop(idx)
                st.session_state.idx_ativo = max(0, idx - 1)
                st.rerun()
        with col_b:
            if st.button("🗑️ Limpar tudo", use_container_width=True):
                st.session_state.talhoes = []
                st.session_state.idx_ativo = 0
                st.session_state.export_pkg = None
                st.rerun()
    else:
        st.info("Nenhum talhão salvo.\nDesenhe na aba **Talhões**.")
        