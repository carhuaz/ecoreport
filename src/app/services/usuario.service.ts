import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { Usuario, RolUsuario } from '../models/usuario.model';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class UsuarioService {
  constructor(private authService: AuthService) {}

  obtenerUsuarios(): Observable<Usuario[]> {
    return this.authService.obtenerTodosLosUsuarios();
  }

  obtenerUsuarioPorId(id: number): Observable<Usuario | undefined> {
    return this.obtenerUsuarios().pipe(
      map(users => users.find(u => u.id === id))
    );
  }

  buscarUsuarios(termino: string): Observable<Usuario[]> {
    return this.obtenerUsuarios().pipe(
      map(users => {
        const t = termino.toLowerCase();
        return users.filter(u =>
          u.nombre.toLowerCase().includes(t) || u.email.toLowerCase().includes(t)
        );
      })
    );
  }

  filtrarPorRol(rol: RolUsuario): Observable<Usuario[]> {
    return this.obtenerUsuarios().pipe(
      map(users => users.filter(u => u.rol === rol))
    );
  }

  cambiarRolUsuario(id: number, nuevoRol: RolUsuario): Observable<boolean> {
    return this.authService.cambiarRolUsuario(id, nuevoRol);
  }

  activarUsuario(id: number): Observable<boolean> {
    return this.authService.cambiarEstadoUsuario(id, true);
  }

  desactivarUsuario(id: number): Observable<boolean> {
    return this.authService.cambiarEstadoUsuario(id, false);
  }
}
