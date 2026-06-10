import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UsuarioService } from '../../services/usuario.service';
import { AuthService } from '../../services/auth.service';
import { Usuario, RolUsuario } from '../../models/usuario.model';

@Component({
  selector: 'app-admin-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-usuarios.component.html',
  styleUrls: ['./admin-usuarios.component.css']
})
export class AdminUsuariosComponent implements OnInit {
  usuarios: Usuario[] = [];
  usuariosFiltrados: Usuario[] = [];

  filtroNombre = '';
  filtroEmail = '';
  filtroRol: RolUsuario | '' = '';

  rolSeleccionadoModal: RolUsuario = 'Ciudadano';
  usuarioSeleccionado: Usuario | null = null;
  mostrarModal = false;
  mostrarConfirmacion = false;
  mensaje = '';
  mensajeEsError = false;

  constructor(
    private usuarioService: UsuarioService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.cargarUsuarios();
  }

  cargarUsuarios(): void {
    this.usuarioService.obtenerUsuarios().subscribe(data => {
      this.usuarios = data;
      this.aplicarFiltros();
    });
  }

  aplicarFiltros(): void {
    let filtered = [...this.usuarios];

    if (this.filtroNombre) {
      filtered = filtered.filter(u =>
        u.nombre.toLowerCase().includes(this.filtroNombre.toLowerCase())
      );
    }

    if (this.filtroEmail) {
      filtered = filtered.filter(u =>
        u.email.toLowerCase().includes(this.filtroEmail.toLowerCase())
      );
    }

    if (this.filtroRol) {
      filtered = filtered.filter(u => u.rol === this.filtroRol);
    }

    this.usuariosFiltrados = filtered;
  }

  onFiltroChange(): void {
    this.aplicarFiltros();
  }

  abrirModalCambiarRol(usuario: Usuario): void {
    if (this.esUsuarioActual(usuario)) {
      this.mostrarMensaje('No puedes cambiar tu propio rol durante la sesión.', true);
      return;
    }

    this.usuarioSeleccionado = usuario;
    this.rolSeleccionadoModal = usuario.rol;
    this.mostrarModal = true;
  }

  cerrarModal(): void {
    this.mostrarModal = false;
    this.usuarioSeleccionado = null;
  }

  confirmarCambiarRol(): void {
    if (!this.usuarioSeleccionado) return;

    if (this.rolSeleccionadoModal === 'Administrador') {
      this.mostrarConfirmacion = true;
      return;
    }

    this.realizarCambioRol();
  }

  realizarCambioRol(): void {
    if (!this.usuarioSeleccionado) return;

    this.usuarioService.cambiarRolUsuario(
      this.usuarioSeleccionado.id,
      this.rolSeleccionadoModal
    ).subscribe(cambioExitoso => {
      this.mostrarConfirmacion = false;
      this.cerrarModal();
      this.cargarUsuarios();
      this.mostrarMensaje(
        cambioExitoso ? 'Rol actualizado correctamente.' : 'No se pudo actualizar el rol.',
        !cambioExitoso
      );
    });
  }

  cambiarEstado(usuario: Usuario): void {
    const accion$ = usuario.activo
      ? this.usuarioService.desactivarUsuario(usuario.id)
      : this.usuarioService.activarUsuario(usuario.id);

    accion$.subscribe(resultado => {
      if (resultado) {
        this.mostrarMensaje(
          usuario.activo ? 'Usuario desactivado correctamente.' : 'Usuario activado correctamente.'
        );
      } else {
        this.mostrarMensaje('No puedes desactivar el usuario de la sesión actual.', true);
      }
      this.cargarUsuarios();
    });
  }

  esUsuarioActual(usuario: Usuario): boolean {
    return this.authService.obtenerUsuarioActual()?.id === usuario.id;
  }

  private mostrarMensaje(texto: string, esError = false): void {
    this.mensaje = texto;
    this.mensajeEsError = esError;
    setTimeout(() => this.mensaje = '', 3000);
  }

  obtenerColorRol(rol: RolUsuario): string {
    switch (rol) {
      case 'Administrador': return 'role-admin';
      case 'Validador': return 'role-validador';
      case 'Ciudadano': return 'role-ciudadano';
      default: return '';
    }
  }

  obtenerColorEstado(activo: boolean): string {
    return activo ? 'estado-activo' : 'estado-inactivo';
  }
}
