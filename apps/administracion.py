#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APP DE ADMINISTRACIÓN
Sistema de Cálculos y Herramientas - Tribunal de Trabajo 2 de Quilmes
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import AuthSystem
from utils.navegacion import mostrar_sidebar_navegacion

# Inicializar sistema de autenticación
auth = AuthSystem()

# Sidebar de navegación
mostrar_sidebar_navegacion('admin')

st.markdown("# ⚙️ ADMINISTRACIÓN DEL SISTEMA")
st.markdown("---")

# Verificar nivel de acceso
if 'usuario' not in st.session_state or st.session_state.usuario.get('nivel') not in ['superadmin', 'admin']:
    st.error("⚠️ Acceso denegado. Solo administradores pueden acceder a esta sección.")
    st.stop()

es_superadmin = st.session_state.usuario.get('nivel') == 'superadmin'
es_admin = st.session_state.usuario.get('nivel') == 'admin'

# Tabs según nivel de acceso
if es_superadmin:
    tabs = st.tabs(["👥 Gestión de Usuarios", "📊 Edición de Datasets", "📈 Reportes de Auditoría"])
    tab1, tab2, tab3 = tabs[0], tabs[1], tabs[2]
else:  # admin
    tab1 = st.tabs(["👥 Gestión de Usuarios"])[0]
    tab2 = None
    tab3 = None

# TAB 1: GESTIÓN DE USUARIOS
with tab1:
    st.markdown("## 👥 Gestión de Usuarios")
    
    subtab1, subtab2, subtab3 = st.tabs(["Crear Usuario", "Ver Usuarios", "Modificar"])
    
    with subtab1:
        st.markdown("### ➕ Crear Nuevo Usuario")
        
        with st.form("form_crear_usuario"):
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_username = st.text_input("Nombre de usuario*", max_chars=50)
                nuevo_nombre = st.text_input("Nombre completo", max_chars=100)
                nuevo_cargo = st.text_input("Cargo en el Tribunal", max_chars=100, 
                                            placeholder="Ej: Juez, Secretario, Prosecretario, Empleado...")
            
            with col2:
                nuevo_password = st.text_input("Contraseña*", type="password", max_chars=50)
                nuevo_email = st.text_input("Email", max_chars=100)
                
                # Niveles según quien crea
                if es_superadmin:
                    opciones_nivel = ["usuario", "admin", "superadmin"]
                    ayuda_nivel = "superadmin: acceso total | admin: gestiona usuarios | usuario: solo usa apps"
                else:  # admin
                    opciones_nivel = ["usuario", "admin"]
                    ayuda_nivel = "admin: gestiona usuarios | usuario: solo usa apps"
                
                nuevo_nivel = st.selectbox("Nivel de acceso*", opciones_nivel, help=ayuda_nivel)
            
            submitted = st.form_submit_button("Crear Usuario", use_container_width=True, type="primary")
            
            if submitted:
                if not nuevo_username or not nuevo_password:
                    st.error("Usuario y contraseña son obligatorios")
                else:
                    exito, mensaje = auth.crear_usuario(
                        username=nuevo_username,
                        password=nuevo_password,
                        nivel=nuevo_nivel,
                        nombre_completo=nuevo_nombre,
                        cargo=nuevo_cargo,
                        email=nuevo_email,
                        creado_por=st.session_state.usuario['username']
                    )
                    
                    if exito:
                        st.success(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)
    
    with subtab2:
        st.markdown("### 📋 Usuarios del Sistema")
        
        usuarios = auth.listar_usuarios()
        
        if usuarios:
            df_usuarios = pd.DataFrame(usuarios)
            df_display = df_usuarios[['username', 'nivel', 'nombre_completo', 'cargo', 'email', 'ultimo_acceso', 'activo']].copy()
            df_display.columns = ['Usuario', 'Nivel', 'Nombre', 'Cargo', 'Email', 'Último Acceso', 'Activo']
            df_display['Activo'] = df_display['Activo'].map({1: '✅', 0: '❌'})
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            st.caption(f"Total de usuarios: {len(usuarios)}")
        else:
            st.info("No hay usuarios en el sistema")
    
    with subtab3:
        st.markdown("### ✏️ Modificar Usuario")
        
        usuarios = auth.listar_usuarios()
        usernames = [u['username'] for u in usuarios]
        
        usuario_sel = st.selectbox("Seleccionar usuario", usernames)
        usuario_data = auth.obtener_usuario(usuario_sel)
        
        if usuario_data:
            # Mostrar datos actuales
            st.info(f"**Nivel actual:** {usuario_data['nivel']} | **Cargo:** {usuario_data.get('cargo', 'N/A')}")
            
            # Editar datos básicos
            st.markdown("#### ✏️ Editar Datos")
            with st.form("form_editar_datos"):
                col_a, col_b = st.columns(2)
                with col_a:
                    nuevo_nombre = st.text_input("Nombre completo", value=usuario_data.get('nombre_completo', ''))
                    nuevo_cargo = st.text_input("Cargo", value=usuario_data.get('cargo', ''))
                with col_b:
                    nuevo_email = st.text_input("Email", value=usuario_data.get('email', ''))
                    if es_superadmin:
                        nuevo_nivel = st.selectbox("Nivel", ["usuario", "admin", "superadmin"], 
                                                   index=["usuario", "admin", "superadmin"].index(usuario_data['nivel']))
                    else:
                        st.text_input("Nivel (no modificable)", value=usuario_data['nivel'], disabled=True)
                        nuevo_nivel = usuario_data['nivel']
                
                if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                    exito, mensaje = auth.modificar_usuario(
                        username=usuario_sel,
                        modificado_por=st.session_state.usuario['username'],
                        nombre_completo=nuevo_nombre,
                        cargo=nuevo_cargo,
                        email=nuevo_email,
                        nivel=nuevo_nivel if es_superadmin else None
                    )
                    if exito:
                        st.success(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            # Solo superadmin puede cambiar contraseñas
            with col1:
                st.markdown("#### 🔑 Cambiar Contraseña")
                if es_superadmin:
                    with st.form("form_cambiar_pass"):
                        nueva_pass = st.text_input("Nueva contraseña", type="password")
                        confirmar_pass = st.text_input("Confirmar contraseña", type="password")
                        
                        if st.form_submit_button("Cambiar Contraseña"):
                            if nueva_pass != confirmar_pass:
                                st.error("Las contraseñas no coinciden")
                            elif nueva_pass:
                                exito, mensaje = auth.cambiar_password(
                                    username=usuario_sel,
                                    nueva_password=nueva_pass,
                                    cambiado_por=st.session_state.usuario['username']
                                )
                                if exito:
                                    st.success(mensaje)
                                else:
                                    st.error(mensaje)
                else:
                    st.warning("⚠️ Solo el Administrador General puede cambiar contraseñas")
            
            # Superadmin y admin pueden eliminar usuarios
            with col2:
                st.markdown("#### 🗑️ Eliminar Usuario")
                if es_superadmin or es_admin:
                    st.warning(f"¿Eliminar usuario **{usuario_sel}**?")
                    
                    if st.button("🗑️ Eliminar", type="secondary", use_container_width=True):
                        exito, mensaje = auth.eliminar_usuario(
                            username=usuario_sel,
                            eliminado_por=st.session_state.usuario['username']
                        )
                        if exito:
                            st.success(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)
                else:
                    st.warning("⚠️ Solo administradores pueden eliminar usuarios")

# TAB 2: EDICIÓN DE DATASETS (solo superadmin)
if tab2 and es_superadmin:
    with tab2:
        st.markdown("## 📊 Edición de Datasets")
    
        datasets = {
            "JUS": "data/Dataset_JUS.csv",
            "IPC": "data/dataset_ipc.csv",
            "RIPTE": "data/dataset_ripte.csv",
            "Pisos Salariales": "data/dataset_pisos.csv",
            "Tasa Activa": "data/dataset_tasa.csv"
        }
    
        dataset_sel = st.selectbox("Seleccionar dataset", list(datasets.keys()))
        archivo = datasets[dataset_sel]
    
        try:
            df = pd.read_csv(archivo, encoding='utf-8')
        
            st.markdown(f"### 📄 {dataset_sel}")
            st.caption(f"📁 `{archivo}` • 📊 {len(df)} filas • 📋 {len(df.columns)} columnas")
        
            st.markdown("---")
              
            # Sistema de edición custom
            st.markdown("#### ✏️ Editor de Datos")
        
            # CSS para compactar filas
            st.markdown("""
            <style>
            /* Compactar contenedores */
            div[data-testid="stVerticalBlock"] > div:has(div[data-testid="column"]) {
                gap: 0.25rem !important;
                margin-bottom: 0.25rem !important;
            }
        
            /* Compactar inputs de texto */
            div[data-testid="stTextInput"] > div {
                margin-bottom: 0 !important;
            }
        
            div[data-testid="stTextInput"] input {
                padding: 0.25rem 0.5rem !important;
                height: 2rem !important;
                font-size: 0.85rem !important;
            }
        
            /* Compactar botones */
            button[kind="secondary"], button[kind="primary"] {
                padding: 0.25rem 0.5rem !important;
                min-height: 2rem !important;
                height: 2rem !important;
                font-size: 0.85rem !important;
            }
        
            /* Compactar separadores */
            hr {
                margin: 0.25rem 0 !important;
            }
        
            /* Compactar texto de filas */
            .compact-text {
                padding: 0.25rem 0.5rem;
                font-size: 0.85rem;
                line-height: 1.5;
                margin: 0;
            }
            </style>
            """, unsafe_allow_html=True)
        
            # Inicializar estado si no existe
            if f'df_edit_{dataset_sel}' not in st.session_state:
                st.session_state[f'df_edit_{dataset_sel}'] = df.copy()
        
            if f'editing_row_{dataset_sel}' not in st.session_state:
                st.session_state[f'editing_row_{dataset_sel}'] = None
        
            # Estado de paginación
            if f'rows_visible_{dataset_sel}' not in st.session_state:
                st.session_state[f'rows_visible_{dataset_sel}'] = 10  # Mostrar 10 inicialmente
        
            df_trabajo = st.session_state[f'df_edit_{dataset_sel}']
            rows_visible = st.session_state[f'rows_visible_{dataset_sel}']
        
            # Botón para agregar nueva fila - Pequeño a la izquierda
            col_btn_agregar, col_espacio = st.columns([1, 5])
            with col_btn_agregar:
                if st.button("➕ Agregar", type="secondary", use_container_width=True, key=f"add_top_{dataset_sel}"):
                    # Crear fila vacía
                    nueva_fila = pd.DataFrame([{col: "" for col in df_trabajo.columns}])
                    # Agregar al INICIO (arriba)
                    df_trabajo = pd.concat([nueva_fila, df_trabajo], ignore_index=True)
                    st.session_state[f'df_edit_{dataset_sel}'] = df_trabajo
                    # Poner en modo edición la nueva fila (índice 0)
                    st.session_state[f'editing_row_{dataset_sel}'] = 0
                    st.rerun()
        
            st.markdown("")  # Pequeño espacio
        
            # ENCABEZADOS DE COLUMNAS
            cols_header = st.columns([0.3] + [2] * len(df_trabajo.columns) + [0.8])
        
            with cols_header[0]:
                st.markdown("<div class='compact-text'><b>#</b></div>", unsafe_allow_html=True)
        
            for col_idx, columna in enumerate(df_trabajo.columns):
                with cols_header[col_idx + 1]:
                    st.markdown(f"<div class='compact-text'><b>{columna}</b></div>", unsafe_allow_html=True)
        
            with cols_header[-1]:
                st.markdown("<div class='compact-text'><b>Acciones</b></div>", unsafe_allow_html=True)
        
            st.markdown("<hr style='margin: 0.3rem 0; border-width: 2px; border-color: #333;'>", unsafe_allow_html=True)
        
            # Mostrar tabla con botones (solo filas visibles)
            if len(df_trabajo) > 0:
                # Determinar cuántas filas mostrar
                filas_a_mostrar = min(rows_visible, len(df_trabajo))
            
                for idx in range(filas_a_mostrar):
                    cols = st.columns([0.3] + [2] * len(df_trabajo.columns) + [0.8])
                
                    # Número de fila
                    with cols[0]:
                        st.markdown(f"<div class='compact-text'><b>{idx}</b></div>", unsafe_allow_html=True)
                
                    # Si está editando esta fila
                    if st.session_state[f'editing_row_{dataset_sel}'] == idx:
                        # Modo edición
                        nuevos_valores = {}
                        for col_idx, columna in enumerate(df_trabajo.columns):
                            with cols[col_idx + 1]:
                                valor_actual = df_trabajo.iloc[idx][columna]
                                nuevos_valores[columna] = st.text_input(
                                    columna,
                                    value=str(valor_actual) if pd.notna(valor_actual) else "",
                                    key=f"edit_{dataset_sel}_{idx}_{columna}",
                                    label_visibility="collapsed"
                                )
                    
                        # Botones de acción
                        with cols[-1]:
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.button("✅", key=f"save_{dataset_sel}_{idx}", help="Guardar"):
                                    # Actualizar fila
                                    for col, val in nuevos_valores.items():
                                        df_trabajo.at[idx, col] = val
                                    st.session_state[f'df_edit_{dataset_sel}'] = df_trabajo
                                    st.session_state[f'editing_row_{dataset_sel}'] = None
                                    st.rerun()
                        
                            with col_cancel:
                                if st.button("❌", key=f"cancel_{dataset_sel}_{idx}", help="Cancelar"):
                                    st.session_state[f'editing_row_{dataset_sel}'] = None
                                    st.rerun()
                    else:
                        # Modo visualización
                        for col_idx, columna in enumerate(df_trabajo.columns):
                            with cols[col_idx + 1]:
                                valor = df_trabajo.iloc[idx][columna]
                                st.markdown(f"<div class='compact-text'>{str(valor) if pd.notna(valor) else ''}</div>", unsafe_allow_html=True)
                    
                        # Botones de acción
                        with cols[-1]:
                            col_edit, col_delete = st.columns(2)
                            with col_edit:
                                if st.button("✏️", key=f"edit_btn_{dataset_sel}_{idx}", help="Editar"):
                                    st.session_state[f'editing_row_{dataset_sel}'] = idx
                                    st.rerun()
                        
                            with col_delete:
                                if st.button("🗑️", key=f"delete_{dataset_sel}_{idx}", help="Eliminar"):
                                    df_trabajo = df_trabajo.drop(idx).reset_index(drop=True)
                                    st.session_state[f'df_edit_{dataset_sel}'] = df_trabajo
                                    st.rerun()
                
                    st.markdown("<hr style='margin: 0.15rem 0; border-color: #e0e0e0;'>", unsafe_allow_html=True)
            
                # Botones de paginación
                total_filas = len(df_trabajo)
                if total_filas > 10:
                    st.markdown("")  # Espacio
                
                    col_pag1, col_pag2, col_pag3, col_pag4 = st.columns([2, 2, 2, 4])
                
                    with col_pag1:
                        # Botón cargar 10 más
                        if rows_visible < total_filas:
                            if st.button("⬇️ Cargar 10 más", use_container_width=True, key=f"load_more_{dataset_sel}"):
                                st.session_state[f'rows_visible_{dataset_sel}'] = min(rows_visible + 10, total_filas)
                                st.rerun()
                
                    with col_pag2:
                        # Botón mostrar todo
                        if rows_visible < total_filas:
                            if st.button("📄 Mostrar Todo", use_container_width=True, key=f"show_all_{dataset_sel}"):
                                st.session_state[f'rows_visible_{dataset_sel}'] = total_filas
                                st.rerun()
                
                    with col_pag3:
                        # Botón colapsar
                        if rows_visible > 10:
                            if st.button("⬆️ Mostrar menos", use_container_width=True, key=f"collapse_{dataset_sel}"):
                                st.session_state[f'rows_visible_{dataset_sel}'] = 10
                                st.rerun()
                
                    with col_pag4:
                        st.caption(f"Mostrando {rows_visible} de {total_filas} filas")
        
            else:
                st.info("📝 No hay datos. Usa el botón '➕ Agregar' de arriba para comenzar.")
        
            st.markdown("---")
        
            # Botones de acción
            col1, col2, col3 = st.columns([2, 2, 6])
        
            with col1:
                if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
                    try:
                        df_trabajo = st.session_state[f'df_edit_{dataset_sel}']
                    
                        # Ordenar según el tipo de dataset
                        if dataset_sel == "Tasa Activa":
                            # Mantener orden descendente por fecha
                            if 'Desde' in df_trabajo.columns:
                                df_trabajo['Desde'] = pd.to_datetime(
                                    df_trabajo['Desde'],
                                    dayfirst=True,
                                    format='mixed'
                                )
                                df_trabajo = df_trabajo.sort_values('Desde', ascending=False)
                    
                        df_trabajo.to_csv(archivo, index=False, encoding='utf-8')
                        st.success("✅ Cambios guardados exitosamente")
                    
                        # Resetear estado
                        del st.session_state[f'df_edit_{dataset_sel}']
                        del st.session_state[f'editing_row_{dataset_sel}']
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al guardar: {str(e)}")
        
            with col2:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar",
                    data=csv,
                    file_name=f"{dataset_sel}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
            with col3:
                if st.button("🔄 Recargar Original", use_container_width=True):
                    # Resetear a los datos originales
                    if f'df_edit_{dataset_sel}' in st.session_state:
                        del st.session_state[f'df_edit_{dataset_sel}']
                    if f'editing_row_{dataset_sel}' in st.session_state:
                        del st.session_state[f'editing_row_{dataset_sel}']
                    st.rerun()
    
        except Exception as e:
            st.error(f"❌ Error al cargar dataset: {str(e)}")
            st.exception(e)

# TAB 3: REPORTES DE AUDITORÍA (solo superadmin)
if tab3 and es_superadmin:
    with tab3:
        st.markdown("## 📈 Reportes de Auditoría")
        
        subtab_rep1, subtab_rep2, subtab_rep3 = st.tabs(["🔐 Logins", "👥 Acciones Usuarios", "📊 Acciones Tablas"])
        
        with subtab_rep1:
            st.markdown("### 🔐 Historial de Logins")
            
            limit = st.slider("Cantidad de registros", 10, 500, 100)
            
            logins = auth.obtener_reporte_logins(limit=limit)
            
            if logins:
                df_logins = pd.DataFrame(logins)
                df_logins['fecha_hora'] = pd.to_datetime(df_logins['fecha_hora']).dt.strftime('%d/%m/%Y %H:%M:%S')
                df_logins['exito'] = df_logins['exito'].map({True: '✅ Exitoso', False: '❌ Fallido'})
                df_logins = df_logins.rename(columns={
                    'username': 'Usuario',
                    'fecha_hora': 'Fecha/Hora',
                    'exito': 'Resultado',
                    'ip_address': 'IP'
                })
                
                st.dataframe(df_logins[['Usuario', 'Fecha/Hora', 'Resultado', 'IP']], use_container_width=True, hide_index=True)
                
                # Estadísticas
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                with col_stats1:
                    total = len(df_logins)
                    st.metric("Total Intentos", total)
                with col_stats2:
                    exitosos = len(df_logins[df_logins['Resultado'] == '✅ Exitoso'])
                    st.metric("Exitosos", exitosos, delta=f"{(exitosos/total*100):.1f}%")
                with col_stats3:
                    fallidos = len(df_logins[df_logins['Resultado'] == '❌ Fallido'])
                    st.metric("Fallidos", fallidos, delta=f"{(fallidos/total*100):.1f}%", delta_color="inverse")
                
                # Descargar CSV
                csv = df_logins.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Descargar Reporte CSV",
                    csv,
                    f"reporte_logins_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv"
                )
            else:
                st.info("No hay registros de logins")
        
        with subtab_rep2:
            st.markdown("### 👥 Acciones sobre Usuarios")
            
            limit2 = st.slider("Cantidad de registros", 10, 500, 100, key="limit_usuarios")
            
            acciones_usuarios = auth.obtener_reporte_acciones(limit=limit2, tipo="usuario")
            
            if acciones_usuarios:
                df_acc_usr = pd.DataFrame(acciones_usuarios)
                df_acc_usr['fecha_hora'] = pd.to_datetime(df_acc_usr['fecha_hora']).dt.strftime('%d/%m/%Y %H:%M:%S')
                
                # Mapear acciones a emojis
                emoji_map = {'crear': '➕', 'modificar': '✏️', 'eliminar': '🗑️'}
                df_acc_usr['accion_emoji'] = df_acc_usr['accion'].map(emoji_map) + ' ' + df_acc_usr['accion'].str.capitalize()
                
                df_acc_usr = df_acc_usr.rename(columns={
                    'fecha_hora': 'Fecha/Hora',
                    'usuario': 'Realizado Por',
                    'accion_emoji': 'Acción',
                    'objetivo': 'Usuario Afectado',
                    'detalle': 'Detalle'
                })
                
                st.dataframe(df_acc_usr[['Fecha/Hora', 'Realizado Por', 'Acción', 'Usuario Afectado', 'Detalle']], 
                            use_container_width=True, hide_index=True)
                
                # Estadísticas
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    creados = len(df_acc_usr[df_acc_usr['Acción'].str.contains('Crear')])
                    st.metric("➕ Usuarios Creados", creados)
                with col_s2:
                    modificados = len(df_acc_usr[df_acc_usr['Acción'].str.contains('Modificar')])
                    st.metric("✏️ Usuarios Modificados", modificados)
                with col_s3:
                    eliminados = len(df_acc_usr[df_acc_usr['Acción'].str.contains('Eliminar')])
                    st.metric("🗑️ Usuarios Eliminados", eliminados)
                
                # Descargar CSV
                csv2 = df_acc_usr.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Descargar Reporte CSV",
                    csv2,
                    f"reporte_acciones_usuarios_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv"
                )
            else:
                st.info("No hay registros de acciones sobre usuarios")
        
        with subtab_rep3:
            st.markdown("### 📊 Acciones sobre Tablas/Datasets")
            
            limit3 = st.slider("Cantidad de registros", 10, 500, 100, key="limit_tablas")
            
            acciones_tablas = auth.obtener_reporte_acciones(limit=limit3, tipo="tabla")
            
            if acciones_tablas:
                df_acc_tab = pd.DataFrame(acciones_tablas)
                df_acc_tab['fecha_hora'] = pd.to_datetime(df_acc_tab['fecha_hora']).dt.strftime('%d/%m/%Y %H:%M:%S')
                
                df_acc_tab = df_acc_tab.rename(columns={
                    'fecha_hora': 'Fecha/Hora',
                    'usuario': 'Realizado Por',
                    'accion': 'Acción',
                    'objetivo': 'Tabla',
                    'detalle': 'Detalle'
                })
                
                df_acc_tab['Acción'] = df_acc_tab['Acción'].str.capitalize()
                
                st.dataframe(df_acc_tab[['Fecha/Hora', 'Realizado Por', 'Acción', 'Tabla', 'Detalle']], 
                            use_container_width=True, hide_index=True)
                
                # Descargar CSV
                csv3 = df_acc_tab.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Descargar Reporte CSV",
                    csv3,
                    f"reporte_acciones_tablas_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv"
                )
            else:
                st.info("No hay registros de acciones sobre tablas")

st.markdown("---")
st.caption("**Administración del Sistema** | Tribunal de Trabajo N° 2 de Quilmes")