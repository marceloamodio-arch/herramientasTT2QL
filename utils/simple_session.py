"""
Gestor de sesiones persistentes - Sistema Simple
Token en URL + Archivo JSON
"""

import json
import hashlib
import os
from datetime import datetime

class SimpleSessionManager:
    """Gestiona sesiones usando tokens en URL y archivo JSON"""
    
    def __init__(self, session_file="data/sessions.json"):
        self.session_file = session_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Crear archivo de sesiones si no existe"""
        if not os.path.exists(self.session_file):
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            self._save_sessions({})
    
    def _load_sessions(self):
        """Cargar sesiones desde archivo"""
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_sessions(self, sessions):
        """Guardar sesiones en archivo"""
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
    
    def create_session(self, username):
        """
        Crea una nueva sesión y retorna el token
        
        Args:
            username: Nombre de usuario
            
        Returns:
            token: Token único de 16 caracteres
        """
        sessions = self._load_sessions()
        
        # Generar token único y corto
        timestamp = datetime.now().isoformat()
        token = hashlib.sha256(f"{username}{timestamp}".encode()).hexdigest()[:16]
        
        # Guardar sesión
        sessions[token] = {
            'username': username,
            'created': timestamp,
            'last_access': timestamp
        }
        
        self._save_sessions(sessions)
        return token
    
    def get_session(self, token):
        """
        Obtiene datos de sesión por token
        
        Args:
            token: Token de sesión
            
        Returns:
            username o None si no existe
        """
        sessions = self._load_sessions()
        
        if token in sessions:
            # Actualizar último acceso
            sessions[token]['last_access'] = datetime.now().isoformat()
            self._save_sessions(sessions)
            
            return sessions[token]['username']
        
        return None
    
    def delete_session(self, token):
        """
        Elimina una sesión
        
        Args:
            token: Token de sesión a eliminar
        """
        sessions = self._load_sessions()
        
        if token in sessions:
            del sessions[token]
            self._save_sessions(sessions)
    
    def delete_user_sessions(self, username):
        """
        Elimina todas las sesiones de un usuario
        
        Args:
            username: Nombre de usuario
        """
        sessions = self._load_sessions()
        
        # Filtrar sesiones que no sean del usuario
        sessions = {
            token: data for token, data in sessions.items()
            if data['username'] != username
        }
        
        self._save_sessions(sessions)
