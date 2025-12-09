"""
Utilidades compartidas del Sistema de Cálculos y Herramientas
Tribunal de Trabajo 2 de Quilmes
"""

from .data_loader import (
    DataLoader,
    cargar_dataset_jus,
    cargar_dataset_ipc,
    cargar_dataset_pisos,
    cargar_dataset_ripte,
    cargar_dataset_tasa,
    get_ultimo_dato
)

from .auth import AuthSystem
from .simple_session import SimpleSessionManager
from .navegacion import mostrar_sidebar_navegacion

__all__ = [
    'DataLoader',
    'cargar_dataset_jus',
    'cargar_dataset_ipc',
    'cargar_dataset_pisos',
    'cargar_dataset_ripte',
    'cargar_dataset_tasa',
    'get_ultimo_dato',
    'AuthSystem',
    'SimpleSessionManager',
    'mostrar_sidebar_navegacion'
]