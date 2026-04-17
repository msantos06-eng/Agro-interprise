import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.export_utils import brand_package_multi


st.header("📤 Exportar para Máquinas Agrícolas")

if "talhoes" not in st.session_state or not st.session_state.talhoes:
    st.warning("Nenhum talhão carregado.")
else:
    st.success("Pronto para exportar")

    # ✅ CRIA AS COLUNAS ANTES DE USAR
    col_brand, col_dl = st.columns(2)

    with col_brand:
        st.write("Configuração aqui")

    with col_dl:
        st.write("Download aqui")

        brand_opts = {
            'John Deere': '🟢 Operations Center / GS3 / GS4 / Gen4',
            'CNH':        '🔴 AFS Connect (Case) · PLM Intelligence (NH)',
            'Jacto':      '🔵 Jacto Connected / JD100 / JD5000',
            'Fendt':      '⚪ VarioDoc / AGCO Connect / VARIOTERMINAL',
            'Valtra':     '🟡 Valtra Connect / SmartTouch',
        }

        selected = st.selectbox("Marca", list(brand_opts.keys()))
        st.info(brand_opts[selected])

        st.subheader("Talhões a exportar")

        sel_talhoes = []
        for i, t in enumerate(st.session_state.talhoes):
            tem_dados = any([
                t.get('grid_cells'),
                t.get('vra_cells'),
                t.get('lines')
            ])

            check = st.checkbox(
                f"{t['nome']} -- {t['stats']['area_ha']} ha"
                + (" ✅" if tem_dados else " (apenas limite)"),
                value=True,
                key=f"exp_{i}"
            )

            if check:
                sel_talhoes.append(t)

        if st.button(
            f"📦 Gerar pacote para {selected}",
            type="primary",
            use_container_width=True,
            disabled=not sel_talhoes
        ):
            with st.spinner("Gerando pacote..."):
                try:
                    pkg = brand_package_multi(sel_talhoes, selected)

                    st.session_state.export_pkg = pkg
                    st.session_state.export_brand = selected

                    st.success(f"Pacote com {len(sel_talhoes)} talhão(ões) gerado!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro: {e}")

    # ---------------- COLUNA DIREITA ----------------
    with col_dl:
        st.subheader("Download")

        if "export_pkg" in st.session_state and st.session_state.export_pkg:
            brand = st.session_state.export_brand

            st.download_button(
                label=f"⬇️ Baixar pacote {brand} (.zip)",
                data=st.session_state.export_pkg,
                file_name=f"agroforce_{brand.lower().replace(' ','_')}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary",
            )

            st.success("Pacote pronto! O ZIP contém uma pasta por talhão.")

        else:
            st.info("Configure e gere o pacote ao lado.")

        st.divider()
        st.subheader("Resumo dos talhões")

        df = pd.DataFrame([
            {
                'Nome': t['nome'],
                'Área (ha)': t['stats']['area_ha'],
                'Grade': '✅' if t.get('grid_cells') else '--',
                'VRA': '✅' if t.get('vra_cells') else '--',
                'Linhas': '✅' if t.get('lines') else '--',
                'Buffer': '✅' if t.get('buffer_geom') else '--',
            }
            for t in st.session_state.talhoes
        ])

        st.dataframe(df, use_container_width=True, hide_index=True)

        total_ha = sum(t['stats']['area_ha'] for t in st.session_state.talhoes)
        st.metric("Área total de todos os talhões", f"{total_ha:.2f} ha")