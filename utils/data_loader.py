#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Cálculos y Herramientas - Tribunal de Trabajo 2 de Quilmes
Módulo: Data Loader - Carga centralizada de datasets

Este módulo centraliza la carga de todos los datasets utilizados
en el sistema, proporcionando funciones reutilizables y manejo de errores.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
import streamlit as st
from datetime import datetime

class DataLoader:
    """Clase para cargar y gestionar datasets del sistema"""
    
    # Rutas base
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    
    # Nombres de archivos
    DATASETS = {
        'jus': 'Dataset_JUS.csv',
        'ipc': 'dataset_ipc.csv',
        'pisos': 'dataset_pisos.csv',
        'ripte': 'dataset_ripte.csv',
        'tasa': 'dataset_tasa.csv'
    }
    
    @staticmethod
    def get_ultimo_dato(df):
        """
        Obtiene el dato más reciente de cualquier dataset.
        
        IMPORTANTE: Todos los datasets están ordenados con el dato más reciente ARRIBA (fila 0).
        Esto incluye: RIPTE, IPC, JUS, Pisos y Tasa Activa.
        
        Args:
            df: DataFrame con datos ordenados (más reciente arriba)
            
        Returns:
            Series con el último dato (más reciente)
            
        Ejemplo:
            ultimo_ripte = DataLoader.get_ultimo_dato(df_ripte)
            valor = ultimo_ripte['indice_ripte']
        """
        if df.empty:
            return None
        return df.iloc[0]  # Primer fila = más reciente
    
    def __init__(self):
        """Inicializa el cargador de datos"""
        self._cache = {}
        self._verificar_estructura()
    
    def _verificar_estructura(self):
        """Verifica que exista la estructura de carpetas necesaria"""
        if not self.DATA_DIR.exists():
            raise FileNotFoundError(
                f"No se encuentra la carpeta 'data' en {self.BASE_DIR}. "
                "Ejecuta el script de migración: python migrate_structure.py"
            )
    
    def _obtener_ruta(self, dataset_key: str) -> Path:
        """
        Obtiene la ruta completa de un dataset
        
        Args:
            dataset_key: Clave del dataset ('jus', 'ipc', 'pisos', 'ripte', 'tasa')
        
        Returns:
            Path: Ruta completa al archivo CSV
        """
        if dataset_key not in self.DATASETS:
            raise ValueError(
                f"Dataset '{dataset_key}' no reconocido. "
                f"Opciones válidas: {list(self.DATASETS.keys())}"
            )
        
        return self.DATA_DIR / self.DATASETS[dataset_key]
    
    @st.cache_data(ttl=3600)  # Cache por 1 hora
    def cargar_dataset(_self, dataset_key: str, **kwargs) -> pd.DataFrame:
        """
        Carga un dataset desde el directorio data/
        
        Args:
            dataset_key: Clave del dataset a cargar
            **kwargs: Argumentos adicionales para pd.read_csv()
        
        Returns:
            DataFrame con los datos cargados
        
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si la clave del dataset no es válida
        """
        ruta = _self._obtener_ruta(dataset_key)
        
        if not ruta.exists():
            raise FileNotFoundError(
                f"No se encuentra el archivo: {ruta}\n"
                f"Verifica que el dataset '{dataset_key}' esté en la carpeta data/"
            )
        
        try:
            # Configuración por defecto para cada dataset
            config_defecto = _self._obtener_config_defecto(dataset_key)
            config_defecto.update(kwargs)
            
            df = pd.read_csv(ruta, **config_defecto)
            
            # Post-procesamiento específico por dataset
            df = _self._procesar_dataset(df, dataset_key)
            
            return df
        
        except Exception as e:
            raise Exception(f"Error al cargar {dataset_key}: {str(e)}")
    
    def _obtener_config_defecto(self, dataset_key: str) -> Dict[str, Any]:
        """
        Obtiene la configuración por defecto para cada dataset
        
        Args:
            dataset_key: Clave del dataset
        
        Returns:
            Diccionario con configuración para pd.read_csv()
        """
        configs = {
            'jus': {
                'encoding': 'utf-8',
                'parse_dates': ['Fecha'] if 'Fecha' in self._peek_columns(dataset_key) else []
            },
            'ipc': {
                'encoding': 'utf-8',
                'parse_dates': ['Fecha'] if 'Fecha' in self._peek_columns(dataset_key) else []
            },
            'pisos': {
                'encoding': 'utf-8',
                'parse_dates': ['Fecha'] if 'Fecha' in self._peek_columns(dataset_key) else []
            },
            'ripte': {
                'encoding': 'utf-8',
                'parse_dates': ['Fecha'] if 'Fecha' in self._peek_columns(dataset_key) else []
            },
            'tasa': {
                'encoding': 'utf-8',
                'parse_dates': ['Fecha'] if 'Fecha' in self._peek_columns(dataset_key) else []
            }
        }
        
        return configs.get(dataset_key, {'encoding': 'utf-8'})
    
    def _peek_columns(self, dataset_key: str) -> list:
        """
        Obtiene los nombres de columnas sin cargar todo el dataset
        
        Args:
            dataset_key: Clave del dataset
        
        Returns:
            Lista con nombres de columnas
        """
        ruta = self._obtener_ruta(dataset_key)
        try:
            return pd.read_csv(ruta, nrows=0).columns.tolist()
        except:
            return []
    
    def _procesar_dataset(self, df: pd.DataFrame, dataset_key: str) -> pd.DataFrame:
        """
        Aplica procesamiento específico a cada dataset después de cargarlo
        
        Args:
            df: DataFrame cargado
            dataset_key: Clave del dataset
        
        Returns:
            DataFrame procesado
        """
        # Procesamiento específico por dataset
        if dataset_key == 'jus':
            # Asegurar que las fechas estén en formato correcto
            if 'Fecha' in df.columns:
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        
        elif dataset_key == 'ipc':
            if 'Fecha' in df.columns:
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
            # Ordenar por fecha
            if 'Fecha' in df.columns:
                df = df.sort_values('Fecha')
        
        elif dataset_key == 'ripte':
            if 'Fecha' in df.columns:
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
            if 'Fecha' in df.columns:
                df = df.sort_values('Fecha')
        
        # Eliminar duplicados
        df = df.drop_duplicates()
        
        # Resetear índice
        df = df.reset_index(drop=True)
        
        return df
    
    def cargar_jus(self) -> pd.DataFrame:
        """Carga el dataset de índice JUS"""
        return self.cargar_dataset('jus')
    
    def cargar_ipc(self) -> pd.DataFrame:
        """Carga el dataset de IPC"""
        return self.cargar_dataset('ipc')
    
    def cargar_pisos(self) -> pd.DataFrame:
        """Carga el dataset de pisos salariales"""
        return self.cargar_dataset('pisos')
    
    def cargar_ripte(self) -> pd.DataFrame:
        """Carga el dataset de RIPTE"""
        return self.cargar_dataset('ripte')
    
    def cargar_tasa(self) -> pd.DataFrame:
        """Carga el dataset de tasa activa"""
        return self.cargar_dataset('tasa')
    
    def obtener_info_datasets(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene información sobre todos los datasets disponibles
        
        Returns:
            Diccionario con información de cada dataset
        """
        info = {}
        
        for key, filename in self.DATASETS.items():
            ruta = self.DATA_DIR / filename
            
            if ruta.exists():
                try:
                    df = self.cargar_dataset(key)
                    info[key] = {
                        'nombre': filename,
                        'existe': True,
                        'filas': len(df),
                        'columnas': len(df.columns),
                        'tamaño': f"{ruta.stat().st_size / 1024:.2f} KB",
                        'ultima_modificacion': datetime.fromtimestamp(
                            ruta.stat().st_mtime
                        ).strftime('%Y-%m-%d %H:%M'),
                        'columnas_lista': df.columns.tolist()
                    }
                except Exception as e:
                    info[key] = {
                        'nombre': filename,
                        'existe': True,
                        'error': str(e)
                    }
            else:
                info[key] = {
                    'nombre': filename,
                    'existe': False
                }
        
        return info
    
    def validar_datasets(self) -> Dict[str, bool]:
        """
        Valida que todos los datasets estén disponibles y sean válidos
        
        Returns:
            Diccionario con el estado de validación de cada dataset
        """
        validacion = {}
        
        for key in self.DATASETS.keys():
            try:
                df = self.cargar_dataset(key)
                validacion[key] = len(df) > 0
            except:
                validacion[key] = False
        
        return validacion


# Funciones helper para mantener compatibilidad con código existente
def cargar_dataset_jus() -> pd.DataFrame:
    """Función helper para cargar dataset JUS"""
    loader = DataLoader()
    return loader.cargar_jus()

def cargar_dataset_ipc() -> pd.DataFrame:
    """Función helper para cargar dataset IPC"""
    loader = DataLoader()
    return loader.cargar_ipc()

def cargar_dataset_pisos() -> pd.DataFrame:
    """Función helper para cargar dataset de pisos salariales"""
    loader = DataLoader()
    return loader.cargar_pisos()

def cargar_dataset_ripte() -> pd.DataFrame:
    """Función helper para cargar dataset RIPTE"""
    loader = DataLoader()
    return loader.cargar_ripte()

def cargar_dataset_tasa() -> pd.DataFrame:
    """Función helper para cargar dataset de tasa activa"""
    loader = DataLoader()
    return loader.cargar_tasa()


def get_ultimo_dato(df):
    """
    Función helper standalone para obtener el dato más reciente.
    
    IMPORTANTE: Todos los datasets están ordenados con el dato más reciente ARRIBA (fila 0).
    
    Args:
        df: DataFrame con datos ordenados (más reciente arriba)
        
    Returns:
        Series con el último dato (más reciente), o None si está vacío
        
    Ejemplo:
        ultimo_ripte = get_ultimo_dato(df_ripte)
        valor = ultimo_ripte['indice_ripte']
    """
    return DataLoader.get_ultimo_dato(df)


# Ejemplo de uso
if __name__ == '__main__':
    # Crear instancia del cargador
    loader = DataLoader()
    
    # Obtener información de datasets
    print("=" * 80)
    print("INFORMACIÓN DE DATASETS")
    print("=" * 80)
    
    info = loader.obtener_info_datasets()
    for key, data in info.items():
        print(f"\n📊 Dataset: {key.upper()}")
        print(f"   Archivo: {data.get('nombre', 'N/A')}")
        print(f"   Existe: {'✅' if data.get('existe') else '❌'}")
        
        if data.get('existe') and 'filas' in data:
            print(f"   Filas: {data['filas']}")
            print(f"   Columnas: {data['columnas']}")
            print(f"   Tamaño: {data['tamaño']}")
            print(f"   Última modificación: {data['ultima_modificacion']}")
    
    # Validar datasets
    print("\n" + "=" * 80)
    print("VALIDACIÓN DE DATASETS")
    print("=" * 80)
    
    validacion = loader.validar_datasets()
    for key, valido in validacion.items():
        estado = "✅ VÁLIDO" if valido else "❌ INVÁLIDO"
        print(f"{key.upper()}: {estado}")
