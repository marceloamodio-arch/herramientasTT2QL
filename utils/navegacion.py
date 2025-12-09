#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULO DE NAVEGACION ENTRE APPS
Sistema de Calculos y Herramientas - Tribunal de Trabajo 2 de Quilmes
"""

import streamlit as st

def mostrar_sidebar_navegacion(app_actual=None):
    """
    Muestra sidebar de navegacion usando componentes nativos de Streamlit.
    
    Args:
        app_actual: Key de la app actual para resaltarla
    """
    
    with st.sidebar:
        # CSS para logo y título
        st.markdown("""
        <style>
            section[data-testid="stSidebar"] > div {
                padding-top: 0.5vh !important;
                overflow-y: hidden !important;
                max-height: 100vh !important;
                display: flex !important;
                flex-direction: column !important;
            }
            .logo-titulo {
                text-align: center;
                margin-bottom: 0.5vh;
            }
            .logo-titulo h1 {
                font-size: min(2rem, 4vh);
                margin: 0;
                line-height: 1;
            }
            .logo-titulo p {
                font-size: min(0.65rem, 1.5vh);
                margin: 0;
                line-height: 0.9;
                color: #aaa;
            }
            /* Botones responsive */
            .stButton > button {
                padding: min(0.15rem, 0.5vh) min(0.3rem, 1vw) !important;
                font-size: min(0.75rem, 1.8vh) !important;
                margin: min(0.05rem, 0.3vh) 0 !important;
                line-height: 1 !important;
            }
            /* Divider responsive */
            section[data-testid="stSidebar"] hr {
                margin: min(0.1rem, 0.5vh) 0 !important;
            }
            /* Caption responsive */
            section[data-testid="stSidebar"] .small {
                margin: min(0.05rem, 0.3vh) 0 !important;
                line-height: 1 !important;
                font-size: min(0.7rem, 1.5vh) !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Usuario en encabezado
        if 'usuario' in st.session_state and st.session_state.usuario:
            usuario = st.session_state.usuario
            if usuario['nivel'] == 'superadmin':
                tipo = "(Adm.Gral)"
            elif usuario['nivel'] == 'admin':
                tipo = "(Adm)"
            else:
                tipo = "(Usuario)"
            st.caption(f"👤 {usuario['username']} {tipo}")
        
        # Logo y título
        st.markdown("""
        <div class="logo-titulo">
            <h1>⚖️</h1>
            <p>Sistema de Cálculos y Herramientas</p>
            <p>Tribunal de Trabajo Nro. 2 Quilmes</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Boton Volver
        if st.button("🏠 Volver al Menu", use_container_width=True, type="secondary", key="nav_volver"):
            st.session_state.app_actual = None
            st.rerun()
        
        # Apps
        apps = [
            ('ibm', '💰 IBM'),
            ('actualizacion', '📈 Actualizacion'),
            ('lrt', '🧮 LRT'),
            ('despidos', '📊 Despidos'),
            ('honorarios', '⚖️ Honorarios'),
            ('admin', '⚙️ Admin')
        ]
        
        for app_key, label in apps:
            tipo = "primary" if app_key == app_actual else "secondary"
            if st.button(label, use_container_width=True, type=tipo, key=f"nav_{app_key}"):
                st.session_state.app_actual = app_key
                st.rerun()