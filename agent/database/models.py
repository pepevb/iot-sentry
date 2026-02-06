"""
IoT Sentry - Modelos de Base de Datos SQLAlchemy
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Device(Base):
    """Modelo para dispositivos descubiertos en la red"""
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mac_address = Column(String(17), unique=True, nullable=False, index=True)
    ip_address = Column(String(15), nullable=True)
    hostname = Column(String(255), nullable=True)
    vendor = Column(String(255), nullable=True)  # Fabricante via OUI
    device_type = Column(String(50), nullable=True)  # camera, speaker, bulb, etc.
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    flows = relationship("Flow", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Device(id={self.id}, mac={self.mac_address}, ip={self.ip_address}, vendor={self.vendor})>"

    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'id': self.id,
            'mac_address': self.mac_address,
            'ip_address': self.ip_address,
            'hostname': self.hostname,
            'vendor': self.vendor,
            'device_type': self.device_type,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
        }


class Flow(Base):
    """Modelo para flujos de red capturados"""
    __tablename__ = 'flows'

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False, index=True)
    dest_ip = Column(String(45), nullable=False)  # IPv4 o IPv6
    dest_port = Column(Integer, nullable=True)
    protocol = Column(String(10), nullable=False)  # TCP, UDP, ICMP, etc.

    # Información geográfica
    dest_country = Column(String(100), nullable=True)
    dest_city = Column(String(100), nullable=True)
    dest_lat = Column(Float, nullable=True)
    dest_lon = Column(Float, nullable=True)

    # Métricas
    bytes_sent = Column(Integer, default=0)
    packets_sent = Column(Integer, default=0)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relación
    device = relationship("Device", back_populates="flows")

    def __repr__(self):
        return f"<Flow(id={self.id}, device_id={self.device_id}, dest={self.dest_ip}:{self.dest_port})>"

    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'dest_ip': self.dest_ip,
            'dest_port': self.dest_port,
            'protocol': self.protocol,
            'dest_country': self.dest_country,
            'dest_city': self.dest_city,
            'dest_lat': self.dest_lat,
            'dest_lon': self.dest_lon,
            'bytes_sent': self.bytes_sent,
            'packets_sent': self.packets_sent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class Alert(Base):
    """Modelo para alertas de seguridad/privacidad"""
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # unusual_time, suspicious_destination, high_volume
    severity = Column(String(10), nullable=False)  # low, medium, high
    message = Column(Text, nullable=False)
    alert_metadata = Column(JSON, nullable=True)  # Información adicional en formato JSON
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    acknowledged = Column(Boolean, default=False)

    # Relación
    device = relationship("Device", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, severity={self.severity})>"

    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'metadata': self.alert_metadata,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'acknowledged': self.acknowledged,
        }
