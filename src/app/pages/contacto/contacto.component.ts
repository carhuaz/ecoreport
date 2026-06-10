import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface MensajeContacto {
  codigo: string;
  nombre: string;
  email: string;
  asunto: string;
  mensaje: string;
  fecha: string;
}

@Component({
  selector: 'app-contacto',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './contacto.component.html',
  styleUrls: ['./contacto.component.css']
})
export class ContactoComponent {
  nombre = '';
  email = '';
  asunto = 'Consulta general';
  mensaje = '';
  error = '';
  codigoAtencion = '';

  enviar(): void {
    this.error = '';
    this.codigoAtencion = '';

    if (!this.nombre.trim() || !this.email.trim() || !this.mensaje.trim()) {
      this.error = 'Completa tu nombre, correo y mensaje.';
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email)) {
      this.error = 'Ingresa un correo electrónico válido.';
      return;
    }

    const codigo = `ECO-${Date.now().toString().slice(-6)}`;
    const nuevoMensaje: MensajeContacto = {
      codigo,
      nombre: this.nombre.trim(),
      email: this.email.trim().toLowerCase(),
      asunto: this.asunto,
      mensaje: this.mensaje.trim(),
      fecha: new Date().toISOString()
    };
    const mensajes = this.obtenerMensajes();
    mensajes.push(nuevoMensaje);
    localStorage.setItem('ecoreport_contactos', JSON.stringify(mensajes));

    this.codigoAtencion = codigo;
    this.nombre = '';
    this.email = '';
    this.asunto = 'Consulta general';
    this.mensaje = '';
  }

  private obtenerMensajes(): MensajeContacto[] {
    try {
      return JSON.parse(localStorage.getItem('ecoreport_contactos') || '[]') as MensajeContacto[];
    } catch {
      return [];
    }
  }
}
