#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Autenticación v2
Tribunal de Trabajo 2 de Quilmes
- 3 niveles: superadmin, admin, usuario
- Auditoría completa de acciones
- Campo "cargo" para usuarios
"""

import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional, Tuple, List, Dict

class AuthSystem:
    """Sistema de autenticación con SQLite y auditoría"""
    
    def __init__(self, db_path: str = "data/usuarios.db"):
        """Inicializa el sistema de autenticación"""
        self.db_path = db_path
        self._crear_base_datos()
        self._crear_superadmin_default()
    
    def _crear_base_datos(self):
        """Crea la base de datos y tablas si no existen"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de usuarios con 3 niveles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nivel TEXT NOT NULL CHECK(nivel IN ('superadmin', 'admin', 'usuario')),
                nombre_completo TEXT,
                cargo TEXT,
                email TEXT,
                fecha_creacion TEXT NOT NULL,
                ultimo_acceso TEXT,
                creado_por TEXT,
                activo INTEGER DEFAULT 1,
                primer_login INTEGER DEFAULT 1
            )
        ''')
        
        # Tabla de auditoría de logins
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auditoria_logins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                fecha_hora TEXT NOT NULL,
                exito INTEGER NOT NULL,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')
        
        # Tabla de auditoría de acciones (CRUD usuarios y tablas)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auditoria_acciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL,
                usuario TEXT NOT NULL,
                accion TEXT NOT NULL,
                tipo TEXT NOT NULL,
                detalle TEXT,
                objetivo TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Hashea una contraseña usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _crear_superadmin_default(self):
        """Crea un superadmin por defecto si no existe"""
        if not self.usuario_existe("admin"):
            self.crear_usuario(
                username="admin",
                password="admin123",
                nivel="superadmin",
                nombre_completo="Administrador General",
                cargo="Administrador del Sistema",
                email="admin@tribunal.gob.ar",
                creado_por="SISTEMA"
            )
    
    def registrar_login(self, username: str, exito: bool, ip: str = "", user_agent: str = ""):
        """Registra un intento de login en auditoría"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO auditoria_logins (username, fecha_hora, exito, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, datetime.now().isoformat(), 1 if exito else 0, ip, user_agent))
        
        conn.commit()
        conn.close()
    
    def registrar_accion(self, usuario: str, accion: str, tipo: str, detalle: str = "", objetivo: str = ""):
        """
        Registra una acción administrativa
        accion: 'crear', 'modificar', 'eliminar'
        tipo: 'usuario', 'tabla'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO auditoria_acciones (fecha_hora, usuario, accion, tipo, detalle, objetivo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), usuario, accion, tipo, detalle, objetivo))
        
        conn.commit()
        conn.close()
    
    def crear_usuario(
        self,
        username: str,
        password: str,
        nivel: str = "usuario",
        nombre_completo: str = "",
        cargo: str = "",
        email: str = "",
        creado_por: str = ""
    ) -> Tuple[bool, str]:
        """Crea un nuevo usuario"""
        if len(username) < 3:
            return False, "El nombre de usuario debe tener al menos 3 caracteres"
        
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        if nivel not in ['superadmin', 'admin', 'usuario']:
            return False, "Nivel debe ser 'superadmin', 'admin' o 'usuario'"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            fecha_creacion = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO usuarios (username, password_hash, nivel, nombre_completo, cargo, email, fecha_creacion, creado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, nivel, nombre_completo, cargo, email, fecha_creacion, creado_por))
            
            conn.commit()
            conn.close()
            
            # Registrar en auditoría
            self.registrar_accion(
                usuario=creado_por,
                accion="crear",
                tipo="usuario",
                detalle=f"Usuario: {username}, Nivel: {nivel}, Nombre: {nombre_completo}, Cargo: {cargo}",
                objetivo=username
            )
            
            return True, "Usuario creado exitosamente"
        except sqlite3.IntegrityError:
            return False, "El nombre de usuario ya existe"
        except Exception as e:
            return False, f"Error al crear usuario: {str(e)}"
    
    def usuario_existe(self, username: str) -> bool:
        """Verifica si un usuario existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE username = ?', (username,))
        existe = cursor.fetchone()[0] > 0
        conn.close()
        return existe
    
    def validar_credenciales(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """Valida credenciales y retorna datos del usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self._hash_password(password)
        
        cursor.execute('''
            SELECT id, username, nivel, nombre_completo, cargo, email, activo, primer_login
            FROM usuarios
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        resultado = cursor.fetchone()
        
        if resultado:
            if resultado[6] == 0:  # activo
                conn.close()
                self.registrar_login(username, False)
                return False, None
            
            # Actualizar último acceso
            cursor.execute('''
                UPDATE usuarios
                SET ultimo_acceso = ?
                WHERE username = ?
            ''', (datetime.now().isoformat(), username))
            conn.commit()
            
            usuario_data = {
                'id': resultado[0],
                'username': resultado[1],
                'nivel': resultado[2],
                'nombre_completo': resultado[3],
                'cargo': resultado[4],
                'email': resultado[5],
                'primer_login': resultado[7]
            }
            
            conn.close()
            self.registrar_login(username, True)
            return True, usuario_data
        
        conn.close()
        self.registrar_login(username, False)
        return False, None
    
    def listar_usuarios(self) -> List[Dict]:
        """Lista todos los usuarios"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, nivel, nombre_completo, cargo, email, fecha_creacion, ultimo_acceso, creado_por, activo
            FROM usuarios
            ORDER BY fecha_creacion DESC
        ''')
        
        usuarios = []
        for row in cursor.fetchall():
            usuarios.append({
                'id': row[0],
                'username': row[1],
                'nivel': row[2],
                'nombre_completo': row[3],
                'cargo': row[4],
                'email': row[5],
                'fecha_creacion': row[6],
                'ultimo_acceso': row[7],
                'creado_por': row[8],
                'activo': row[9]
            })
        
        conn.close()
        return usuarios
    
    def obtener_usuario(self, username: str) -> Optional[Dict]:
        """Obtiene datos de un usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, nivel, nombre_completo, cargo, email, fecha_creacion, ultimo_acceso, creado_por, activo
            FROM usuarios
            WHERE username = ?
        ''', (username,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'nivel': row[2],
                'nombre_completo': row[3],
                'cargo': row[4],
                'email': row[5],
                'fecha_creacion': row[6],
                'ultimo_acceso': row[7],
                'creado_por': row[8],
                'activo': row[9]
            }
        return None
    
    def modificar_usuario(
        self,
        username: str,
        modificado_por: str,
        nombre_completo: str = None,
        cargo: str = None,
        email: str = None,
        nivel: str = None,
        activo: int = None
    ) -> Tuple[bool, str]:
        """Modifica datos de un usuario (NO contraseña)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            campos_update = []
            valores = []
            detalle_cambios = []
            
            if nombre_completo is not None:
                campos_update.append("nombre_completo = ?")
                valores.append(nombre_completo)
                detalle_cambios.append(f"nombre_completo: {nombre_completo}")
            
            if cargo is not None:
                campos_update.append("cargo = ?")
                valores.append(cargo)
                detalle_cambios.append(f"cargo: {cargo}")
            
            if email is not None:
                campos_update.append("email = ?")
                valores.append(email)
                detalle_cambios.append(f"email: {email}")
            
            if nivel is not None:
                campos_update.append("nivel = ?")
                valores.append(nivel)
                detalle_cambios.append(f"nivel: {nivel}")
            
            if activo is not None:
                campos_update.append("activo = ?")
                valores.append(activo)
                detalle_cambios.append(f"activo: {activo}")
            
            if not campos_update:
                return False, "No se especificaron cambios"
            
            valores.append(username)
            query = f"UPDATE usuarios SET {', '.join(campos_update)} WHERE username = ?"
            
            cursor.execute(query, valores)
            conn.commit()
            conn.close()
            
            # Registrar en auditoría
            self.registrar_accion(
                usuario=modificado_por,
                accion="modificar",
                tipo="usuario",
                detalle=", ".join(detalle_cambios),
                objetivo=username
            )
            
            return True, "Usuario modificado exitosamente"
        except Exception as e:
            return False, f"Error al modificar usuario: {str(e)}"
    
    def cambiar_password(self, username: str, nueva_password: str, cambiado_por: str) -> Tuple[bool, str]:
        """Cambia la contraseña de un usuario (solo superadmin)"""
        if len(nueva_password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            nuevo_hash = self._hash_password(nueva_password)
            cursor.execute('UPDATE usuarios SET password_hash = ?, primer_login = 0 WHERE username = ?', (nuevo_hash, username))
            
            conn.commit()
            conn.close()
            
            # Registrar en auditoría
            self.registrar_accion(
                usuario=cambiado_por,
                accion="modificar",
                tipo="usuario",
                detalle="Cambio de contraseña",
                objetivo=username
            )
            
            return True, "Contraseña cambiada exitosamente"
        except Exception as e:
            return False, f"Error al cambiar contraseña: {str(e)}"
    
    def eliminar_usuario(self, username: str, eliminado_por: str) -> Tuple[bool, str]:
        """Elimina un usuario (solo superadmin)"""
        if username == "admin":
            return False, "No se puede eliminar el usuario admin"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener datos antes de eliminar para auditoría
            cursor.execute('SELECT nombre_completo, nivel FROM usuarios WHERE username = ?', (username,))
            usuario_data = cursor.fetchone()
            
            cursor.execute('DELETE FROM usuarios WHERE username = ?', (username,))
            conn.commit()
            conn.close()
            
            # Registrar en auditoría
            detalle = f"Usuario eliminado: {usuario_data[0]}, Nivel: {usuario_data[1]}" if usuario_data else ""
            self.registrar_accion(
                usuario=eliminado_por,
                accion="eliminar",
                tipo="usuario",
                detalle=detalle,
                objetivo=username
            )
            
            return True, "Usuario eliminado exitosamente"
        except Exception as e:
            return False, f"Error al eliminar usuario: {str(e)}"
    
    def obtener_reporte_logins(self, limit: int = 100) -> List[Dict]:
        """Obtiene reporte de logins (solo superadmin)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, fecha_hora, exito, ip_address, user_agent
            FROM auditoria_logins
            ORDER BY fecha_hora DESC
            LIMIT ?
        ''', (limit,))
        
        logins = []
        for row in cursor.fetchall():
            logins.append({
                'id': row[0],
                'username': row[1],
                'fecha_hora': row[2],
                'exito': bool(row[3]),
                'ip_address': row[4],
                'user_agent': row[5]
            })
        
        conn.close()
        return logins
    
    def obtener_reporte_acciones(self, limit: int = 100, tipo: str = None) -> List[Dict]:
        """Obtiene reporte de acciones administrativas (solo superadmin)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if tipo:
            cursor.execute('''
                SELECT id, fecha_hora, usuario, accion, tipo, detalle, objetivo
                FROM auditoria_acciones
                WHERE tipo = ?
                ORDER BY fecha_hora DESC
                LIMIT ?
            ''', (tipo, limit))
        else:
            cursor.execute('''
                SELECT id, fecha_hora, usuario, accion, tipo, detalle, objetivo
                FROM auditoria_acciones
                ORDER BY fecha_hora DESC
                LIMIT ?
            ''', (limit,))
        
        acciones = []
        for row in cursor.fetchall():
            acciones.append({
                'id': row[0],
                'fecha_hora': row[1],
                'usuario': row[2],
                'accion': row[3],
                'tipo': row[4],
                'detalle': row[5],
                'objetivo': row[6]
            })
        
        conn.close()
        return acciones