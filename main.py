#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Cálculos y Herramientas
Tribunal de Trabajo 2 de Quilmes

Aplicación principal con autenticación y menú de acceso a todas las herramientas
"""

import streamlit as st
from pathlib import Path
import sys

# Configurar el path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

# Importar módulo de autenticación
from utils.auth import AuthSystem
from utils.simple_session import SimpleSessionManager
from utils.data_loader import get_ultimo_dato

# Configuración de la página
st.set_page_config(
    page_title="Sistema Tribunal de Trabajo 2 Quilmes",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Información de las aplicaciones disponibles
APLICACIONES = {
    "ibm": {
        "nombre": "Calculadora IBM",
        "icono": "💰",
        "descripcion": "Cálculo de Indemnización Base Mensual según normativa laboral vigente",
        "archivo": "apps.ibm",
        "función": "main",
        "nivel_requerido": "normal"
    },
    "actualizacion": {
        "nombre": "Actualización e Intereses",
        "icono": "📈",
        "descripcion": "Actualización de montos mediante índices IPC, RIPTE y tasas de interés",
        "archivo": "apps.actualizacion",
        "función": "main",
        "nivel_requerido": "normal"
    },
    "lrt": {
        "nombre": "Calculadora LRT",
        "icono": "🧮",
        "descripcion": "Cálculo de indemnizaciones según Ley de Riesgos del Trabajo",
        "archivo": "apps.calculadora_lrt",
        "función": "main",
        "nivel_requerido": "normal"
    },
    "despidos": {
        "nombre": "Calculadora de Despidos",
        "icono": "📊",
        "descripcion": "Cálculo de indemnizaciones por despido según tipo y antigüedad",
        "archivo": "apps.calculadora_despidos",
        "función": "main",
        "nivel_requerido": "normal"
    },
    "honorarios": {
        "nombre": "Cálculo de Honorarios",
        "icono": "💵",
        "descripcion": "Determinación de honorarios profesionales según Ley 14.967",
        "archivo": "apps.honorarios",
        "función": "main",
        "nivel_requerido": "normal"
    },
    "admin": {
        "nombre": "Administración",
        "icono": "⚙️",
        "descripcion": "Gestión de usuarios y edición de datasets del sistema",
        "archivo": "apps.administracion",
        "función": "main",
        "nivel_requerido": "admin"
    }
}

# CSS personalizado para el sistema
def load_custom_css():
    st.markdown("""
        <style>
        /* Estilos generales */
        .main-title {
            text-align: center;
            color: #1f4788;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            text-align: center;
            color: #555;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        
        /* Tarjetas de aplicaciones */
        .app-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            border-left: 4px solid #667eea;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .app-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
        }
        
        .app-card h3 {
            color: #1f4788;
            margin-bottom: 0.5rem;
        }
        
        .app-card p {
            color: #666;
            font-size: 0.95rem;
        }
        
        /* Botones */
        .stButton>button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 8px;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
        }
        
        /* Información del footer */
        .footer {
            text-align: center;
            color: #888;
            font-size: 0.85rem;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #eee;
        }
        
        /* Login */
        .login-box {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_login():
    """Muestra pantalla de login"""
    auth = AuthSystem()
    
    # Header
    st.markdown("""
        <div style='text-align: center; padding: 3rem 0 2rem 0;'>
            <h1 style='color: #667eea; font-size: 4rem; margin: 0;'>⚖️</h1>
            <h1 style='color: #1f4788; margin: 1rem 0 0.5rem 0;'>Sistema de Cálculos y Herramientas</h1>
            <p style='color: #666; font-size: 1.1rem;'>Tribunal de Trabajo N° 2 de Quilmes</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Formulario de login centrado
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Iniciar Sesión")
        
        with st.form("login_form"):
            username = st.text_input(
                "Usuario", 
                placeholder="Ingresa tu usuario",
                help="Usuario creado por el administrador"
            )
            password = st.text_input(
                "Contraseña", 
                type="password", 
                placeholder="Ingresa tu contraseña"
            )
            
            submit = st.form_submit_button("🔓 Ingresar", use_container_width=True, type="primary")
            
            if submit:
                if not username or not password:
                    st.error("⚠️ Por favor completa todos los campos")
                else:
                    # Autenticar usuario
                    autenticado, usuario_data = auth.validar_credenciales(username, password)
                    
                    if autenticado:
                        # Guardar usuario en sesión
                        st.session_state.autenticado = True
                        st.session_state.usuario = usuario_data
                        
                        # Verificar si es primer login
                        if usuario_data.get('primer_login', 0) == 1:
                            st.session_state.mostrar_cambio_password = True
                        
                        # Crear token de sesión persistente
                        session_mgr = SimpleSessionManager()
                        token = session_mgr.create_session(username)
                        st.query_params['st'] = token
                        
                        st.success(f"✅ Bienvenido, {usuario_data['nombre_completo'] or usuario_data['username']}!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown('</div>', unsafe_allow_html=True)
       
    # Footer
    st.markdown("""
        <div class='footer'>
            <p>
                <strong>Sistema de Cálculos y Herramientas</strong><br>
                Tribunal de Trabajo N° 2 de Quilmes<br>
                Provincia de Buenos Aires, Argentina
            </p>
        </div>
    """, unsafe_allow_html=True)

def mostrar_header():
    """Muestra el encabezado del sistema cuando está logueado"""
    col1, col2, col3 = st.columns([1, 8, 2])
    
    with col2:
        st.markdown('<h1 class="main-title">Sistema de Cálculos y Herramientas</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Tribunal de Trabajo N° 2 de Quilmes</p>', unsafe_allow_html=True)
    
    with col3:
        usuario = st.session_state.usuario
        st.markdown(f"**👤 {usuario['username']}**")
        st.caption(f"Nivel: {usuario['nivel']}")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
            # Borrar token de sesión si existe
            if 'st' in st.query_params:
                session_mgr = SimpleSessionManager()
                session_mgr.delete_session(st.query_params['st'])
            
            # Limpiar todo
            st.query_params.clear()
            st.session_state.clear()
            st.rerun()
    
    st.markdown("---")

def ejecutar_aplicacion(app_key):
    """Ejecuta la aplicación seleccionada"""
    app_info = APLICACIONES[app_key]
    
    # Verificar permisos
    if app_info['nivel_requerido'] == 'admin' and st.session_state.usuario['nivel'] not in ['admin', 'superadmin']:
        st.error("🚫 No tienes permisos para acceder a esta aplicación. Solo administradores.")
        if st.button("⬅️ Volver al menú"):
            st.session_state.app_actual = None
            st.rerun()
        return
    
    try:
        # Ejecutar la aplicación directamente (sin botón volver ni título - ahora se maneja dentro de cada app)
        import importlib.util
        
        modulo_nombre = app_info['archivo']
        archivo_path = f"{modulo_nombre.replace('.', '/')}.py"
        
        try:
            # Cargar módulo desde archivo
            spec = importlib.util.spec_from_file_location(modulo_nombre, archivo_path)
            modulo = importlib.util.module_from_spec(spec)
            sys.modules[modulo_nombre] = modulo
            
            # Ejecutar el módulo
            spec.loader.exec_module(modulo)
            
        except FileNotFoundError:
            st.error(f"❌ No se encuentra el archivo: {archivo_path}")
            st.info("""
                **Posibles soluciones:**
                1. Verifica que el archivo existe en la carpeta apps/
                2. Asegúrate de haber ejecutado el script de migración
                3. Revisa que el nombre del archivo es correcto
            """)
            
            if st.button("Volver al menú principal"):
                st.session_state.app_actual = None
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error al ejecutar la aplicación: {e}")
            st.exception(e)
            
            if st.button("Volver al menú principal", key="btn_exec_error"):
                st.session_state.app_actual = None
                st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error inesperado: {e}")
        st.exception(e)
        
        if st.button("Volver al menú principal", key="btn_error_volver"):
            st.session_state.app_actual = None
            st.rerun()

def mostrar_menu_principal():
    """Muestra el menú principal con todas las aplicaciones"""
    mostrar_header()
    
    # Mensaje de bienvenida personalizado
    usuario = st.session_state.usuario
    
    st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h3 style='color: #1f4788; margin-top: 0;'>👋 Bienvenido/a, {usuario['nombre_completo'] or usuario['username']}</h3>
            <p style='margin-bottom: 0; color: #555;'>
                Selecciona una de las herramientas disponibles para comenzar a trabajar.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Mostrar aplicaciones disponibles según nivel de usuario
    nivel_usuario = usuario['nivel']
    
    # Filtrar aplicaciones según permisos
    apps_disponibles = {
        k: v for k, v in APLICACIONES.items()
        if v['nivel_requerido'] == 'normal' or nivel_usuario in ['admin', 'superadmin']
    }
    
    st.markdown("### 🛠️ Aplicaciones Disponibles")
    
    # Mostrar aplicaciones en grid de 2 columnas
    apps_list = list(apps_disponibles.items())
    
    for i in range(0, len(apps_list), 2):
        cols = st.columns(2)
        
        for j, col in enumerate(cols):
            if i + j < len(apps_list):
                app_key, app_info = apps_list[i + j]
                with col:
                    with st.container():
                        # Marcar apps de admin
                        admin_badge = " 🔒 ADMIN" if app_info['nivel_requerido'] == 'admin' else ""
                        
                        st.markdown(f"""
                            <div class='app-card'>
                                <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>{app_info['icono']}</div>
                                <h3>{app_info['nombre']}{admin_badge}</h3>
                                <p>{app_info['descripcion']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"Abrir aplicación", key=f"btn_{app_key}", use_container_width=True):
                            st.session_state.app_actual = app_key
                            st.rerun()
    
    # Mostrar últimos datos disponibles - ANTES DEL FOOTER
    try:
        import pandas as pd
        
        # Cargar datasets
        df_ripte = pd.read_csv("data/dataset_ripte.csv", encoding='utf-8')
        
        df_ipc = pd.read_csv("data/dataset_ipc.csv", encoding='utf-8')
        df_ipc['periodo'] = pd.to_datetime(df_ipc['periodo'])
        
        df_tasa = pd.read_csv("data/dataset_tasa.csv", encoding='utf-8')
        df_tasa['Desde'] = pd.to_datetime(df_tasa['Desde'], format='%d/%m/%Y', dayfirst=True)
        df_tasa['Hasta'] = pd.to_datetime(df_tasa['Hasta'], format='%d/%m/%Y', dayfirst=True)
        
        df_jus = pd.read_csv("data/Dataset_JUS.csv", encoding='utf-8')
        
        df_pisos = pd.read_csv("data/dataset_pisos.csv", encoding='utf-8')
        
        # Obtener últimos datos con colores
        textos_datos = []
        
        # RIPTE - Color azul
        if not df_ripte.empty:
            ultimo_ripte = get_ultimo_dato(df_ripte)
            
            # Usar directamente año y mes del dataframe
            año_ripte = ultimo_ripte['año']
            mes_texto = ultimo_ripte['mes']
            
            # Mapear mes texto a número
            meses_map = {
                'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
                'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
                'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12,
                'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4,
                'May': 5, 'Jun': 6, 'Jul': 7, 'Ago': 8,
                'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dic': 12
            }
            
            mes_ripte = meses_map.get(mes_texto[:3], mes_texto) if isinstance(mes_texto, str) else mes_texto
            
            # Intentar diferentes nombres de columna para el valor
            try:
                valor_ripte = ultimo_ripte['índice RIPTE']
            except:
                try:
                    valor_ripte = ultimo_ripte['indice_ripte']
                except:
                    valor_ripte = ultimo_ripte.iloc[2]  # Tercera columna
            
            textos_datos.append(f'<span style="color: #1f77b4; font-weight: 600;">RIPTE {mes_ripte}/{año_ripte}: {valor_ripte:,.0f}</span>')
        
        # IPC - Color verde
        if not df_ipc.empty:
            ultimo_ipc = get_ultimo_dato(df_ipc)
            fecha_ipc = ultimo_ipc['periodo']
            variacion_ipc = ultimo_ipc['variacion_mensual']
            mes_ipc = fecha_ipc.month
            año_ipc = fecha_ipc.year
            textos_datos.append(f'<span style="color: #2ca02c; font-weight: 600;">IPC {mes_ipc}/{año_ipc}: {variacion_ipc:.2f}%</span>')
        
        # TASA - Color naranja
        if not df_tasa.empty:
            ultima_tasa = get_ultimo_dato(df_tasa)
            valor_tasa = ultima_tasa['Valor']
            fecha_hasta = ultima_tasa['Hasta']
            fecha_txt = fecha_hasta.strftime("%d/%m/%Y")
            textos_datos.append(f'<span style="color: #ff7f0e; font-weight: 600;">TASA {fecha_txt}: {valor_tasa:.2f}%</span>')
        
        # JUS - Color morado
        try:
            ultimo_jus = get_ultimo_dato(df_jus)
            fecha_jus = ultimo_jus['FECHA ENTRADA EN VIGENCIA '].strip() if isinstance(ultimo_jus['FECHA ENTRADA EN VIGENCIA '], str) else ultimo_jus['FECHA ENTRADA EN VIGENCIA ']
            valor_jus_str = ultimo_jus['VALOR IUS'].strip()
            acuerdo_jus = ultimo_jus['ACUERDO'].strip()
            
            # Limpiar valor (quitar $ y espacios, convertir a float)
            valor_jus = float(valor_jus_str.replace('$', '').replace('.', '').replace(',', '.').strip())
            
            # Simplificar acuerdo (solo número)
            acuerdo_num = acuerdo_jus.replace('Acuerdo ', '').replace('acuerdo ', '')
            
            textos_datos.append(f'<span style="color: #9467bd; font-weight: 600;">JUS {fecha_jus} - Ac.{acuerdo_num}: ${valor_jus:,.2f}</span>')
        except Exception as e_jus:
            pass
        
        # PISOS - Color rojo
        try:
            ultimo_piso = get_ultimo_dato(df_pisos)
            fecha_inicio = ultimo_piso['fecha_inicio']
            norma_piso = ultimo_piso['norma']
            monto_piso = float(ultimo_piso['monto_minimo'])
            
            textos_datos.append(f'<span style="color: #d62728; font-weight: 600;">PISO desde {fecha_inicio} - {norma_piso}: ${monto_piso:,.2f}</span>')
        except Exception as e_piso:
            pass
        
        # Mostrar alerta solo si hay datos - con fondo crema suave
        if textos_datos:
            st.markdown(f"""
                <div style='background-color: #fffef0; padding: 1rem; border-radius: 8px; border-left: 4px solid #f0ad4e; margin-bottom: 1.5rem; margin-top: 2rem;'>
                    <p style='margin: 0; font-size: 0.95rem;'>
                        <strong style='color: #856404;'>📊 Últimos Datos Disponibles:</strong><br>
                        {' <span style="color: #ccc;">|</span> '.join(textos_datos)}
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        # No mostrar error, simplemente omitir la alerta
        pass
    
    # Footer
    st.markdown("""
        <div class='footer'>
            <p>
                <strong>Sistema de Cálculos y Herramientas - Tribunal de Trabajo N° 2 de Quilmes</strong><br>
                Desarrollado para optimizar las tareas judiciales y administrativas<br>
                © 2024 - Todos los derechos reservados
            </p>
        </div>
    """, unsafe_allow_html=True)

def main():
    """Función principal del sistema"""
    # Cargar estilos CSS
    load_custom_css()
    
    # Inicializar estado de sesión
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    
    if 'app_actual' not in st.session_state:
        st.session_state.app_actual = None
    
    # Restaurar sesión automáticamente si hay token en URL
    if not st.session_state.autenticado and 'st' in st.query_params:
        token = st.query_params['st']
        session_mgr = SimpleSessionManager()
        username = session_mgr.get_session(token)
        
        if username:
            # Token válido - obtener datos del usuario desde BD
            import sqlite3
            try:
                conn = sqlite3.connect('data/usuarios.db')
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM usuarios WHERE username = ? AND activo = 1', (username,))
                user_row = cursor.fetchone()
                conn.close()
                
                if user_row:
                    # Recrear dict de usuario
                    user_dict = {
                        'id': user_row[0],
                        'username': user_row[1],
                        'nivel': user_row[3],
                        'nombre_completo': user_row[4],
                        'email': user_row[5],
                        'fecha_creacion': user_row[6],
                        'ultimo_acceso': user_row[7],
                        'activo': user_row[8]
                    }
                    
                    # Restaurar sesión
                    st.session_state.autenticado = True
                    st.session_state.usuario = user_dict
            except:
                pass
    
    # Verificar autenticación
    if not st.session_state.autenticado:
        mostrar_login()
    else:
        # Verificar si debe cambiar contraseña (primer login)
        if st.session_state.get('mostrar_cambio_password', False):
            st.warning("⚠️ **Primer inicio de sesión detectado**")
            st.info("Por seguridad, debes cambiar tu contraseña antes de continuar.")
            
            with st.form("form_cambio_password_obligatorio"):
                nueva_pass = st.text_input("Nueva contraseña (mínimo 6 caracteres)", type="password")
                confirmar_pass = st.text_input("Confirmar nueva contraseña", type="password")
                
                if st.form_submit_button("🔐 Cambiar Contraseña", use_container_width=True, type="primary"):
                    if not nueva_pass or not confirmar_pass:
                        st.error("❌ Debes completar ambos campos")
                    elif nueva_pass != confirmar_pass:
                        st.error("❌ Las contraseñas no coinciden")
                    elif len(nueva_pass) < 6:
                        st.error("❌ La contraseña debe tener al menos 6 caracteres")
                    else:
                        auth = AuthSystem()
                        exito, mensaje = auth.cambiar_password(
                            username=st.session_state.usuario['username'],
                            nueva_password=nueva_pass,
                            cambiado_por=st.session_state.usuario['username']
                        )
                        
                        if exito:
                            st.success("✅ Contraseña cambiada exitosamente")
                            st.session_state.mostrar_cambio_password = False
                            st.session_state.usuario['primer_login'] = 0
                            st.rerun()
                        else:
                            st.error(f"❌ {mensaje}")
        else:
            # Usuario autenticado - mostrar sistema
            if st.session_state.app_actual:
                ejecutar_aplicacion(st.session_state.app_actual)
            else:
                mostrar_menu_principal()

if __name__ == "__main__":
    main()