#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades para mostrar información de últimos datos de datasets
VERSIÓN: 2025-12-09 v2 - CON DEBUGGING HABILITADO
"""

import streamlit as st
import pandas as pd


def mostrar_ultimos_datos_universal():
    """
    Muestra una alerta informativa con los últimos datos disponibles de TODOS los datasets.
    
    Carga directamente desde los CSV sin depender de data_manager.
    Incluye: RIPTE, IPC, TASA, PISO, JUS
    """
    
    textos_datos = []
    
    # ========== RIPTE ==========
    try:
        df_ripte = pd.read_csv("data/dataset_ripte.csv", encoding='utf-8')
        if not df_ripte.empty:
            ultimo = df_ripte.iloc[0]
            mes = ultimo['mes'].strip()[:3]
            año = ultimo['año']
            valor = ultimo['indice_ripte']
            valor_fmt = f"{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            textos_datos.append(f"RIPTE {mes}/{año}: {valor_fmt}")
    except Exception as e:
        print(f"[INFO_DATASETS] ERROR en RIPTE: {e}")
    
    # ========== IPC ==========
    try:
        df_ipc = pd.read_csv("data/dataset_ipc.csv", encoding='utf-8')
        if not df_ipc.empty:
            ultimo = df_ipc.iloc[0]
            fecha = pd.to_datetime(ultimo['periodo'], format='%Y-%m')
            valor = ultimo['variacion_mensual']
            valor_fmt = f"{valor:.2f}".replace('.', ',')
            textos_datos.append(f"IPC {fecha.month}/{fecha.year}: {valor_fmt}%")
    except Exception as e:
        print(f"[INFO_DATASETS] ERROR en IPC: {e}")
    
    # ========== TASA ACTIVA ==========
    try:
        df_tasa = pd.read_csv("data/dataset_tasa.csv", encoding='utf-8')
        df_tasa['Desde'] = pd.to_datetime(df_tasa['Desde'], format='%d/%m/%Y', dayfirst=True)
        df_tasa['Hasta'] = pd.to_datetime(df_tasa['Hasta'], format='%d/%m/%Y', dayfirst=True)
        if not df_tasa.empty:
            df_tasa = df_tasa.sort_values('Desde', ascending=False)
            ultimo = df_tasa.iloc[0]
            fecha = ultimo['Hasta']
            valor = float(str(ultimo['Valor']).replace(',', '.'))
            valor_fmt = f"{valor:.2f}".replace('.', ',')
            resultado = f"TASA ACTIVA {fecha.strftime('%d/%m/%Y')}: {valor_fmt}%"
            textos_datos.append(resultado)
            print(f"[INFO_DATASETS] TASA OK: {resultado}")
    except Exception as e:
        print(f"[INFO_DATASETS] ERROR en TASA: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    # ========== JUS ==========
    try:
        df_jus = pd.read_csv("data/Dataset_JUS.csv", encoding='utf-8')
        df_jus.columns = df_jus.columns.str.strip()
        if not df_jus.empty:
            ultimo = df_jus.iloc[0]
            fecha_str = ultimo['FECHA ENTRADA EN VIGENCIA'].strip()
            fecha = pd.to_datetime(fecha_str, format='%d/%m/%Y', dayfirst=True)
            valor_str = ultimo['VALOR IUS'].strip().replace('$', '').replace('.', '').replace(',', '.')
            valor = float(valor_str)
            acuerdo = ultimo['ACUERDO'].strip().replace('Acuerdo ', 'Ac.')
            valor_fmt = f"{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            textos_datos.append(f"JUS {fecha.strftime('%d/%m/%Y')} {acuerdo}: $ {valor_fmt}")
    except Exception as e:
        print(f"[INFO_DATASETS] ERROR en JUS: {e}")
    
    # ========== PISO SRT ==========
    try:
        df_pisos = pd.read_csv("data/dataset_pisos.csv", encoding='utf-8')
        df_pisos['fecha_inicio'] = pd.to_datetime(df_pisos['fecha_inicio'], format='%d/%m/%y')
        df_pisos['fecha_fin'] = pd.to_datetime(df_pisos['fecha_fin'], format='%d/%m/%y', errors='coerce')
        if not df_pisos.empty:
            df_pisos = df_pisos.sort_values('fecha_inicio', ascending=False)
            ultimo = df_pisos.iloc[0]
            norma = ultimo['norma']
            desde = ultimo['fecha_inicio']
            hasta = ultimo['fecha_fin']
            monto = float(ultimo['monto_minimo'])
            
            if pd.isna(hasta):
                periodo = f"({desde.strftime('%d/%m/%Y')} - Vigente)"
            else:
                periodo = f"({desde.strftime('%d/%m/%Y')} al {hasta.strftime('%d/%m/%Y')})"
            
            monto_fmt = f"{monto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            textos_datos.append(f"PISO SRT {norma} {periodo}: $ {monto_fmt}")
    except Exception as e:
        print(f"[INFO_DATASETS] ERROR en PISOS: {e}")
    
    # Debug: mostrar qué se va a renderizar
    print(f"[INFO_DATASETS] Total items a mostrar: {len(textos_datos)}")
    for i, texto in enumerate(textos_datos, 1):
        print(f"[INFO_DATASETS]   {i}. {texto}")
    
    # Mostrar alerta solo si hay datos
    if textos_datos:
        lineas_html = "<br>".join(textos_datos)
        
        st.markdown(f"""
        <div style='background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 0.25rem; padding: 0.75rem 1.25rem; margin-bottom: 1rem; color: #155724;'>
            <strong>📊 Últimos Datos Disponibles:</strong><br>
            {lineas_html}
        </div>
        """, unsafe_allow_html=True)


def mostrar_ultimos_datos(data_manager):
    """
    Función de compatibilidad - llama a mostrar_ultimos_datos_universal()
    """
    mostrar_ultimos_datos_universal()
