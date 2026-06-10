export type RolUsuario = 'Ciudadano' | 'Validador' | 'Administrador';

export interface Usuario {
  id: number;
  nombre: string;
  email: string;
  password?: string;
  rol: RolUsuario;
  activo: boolean;
  fechaRegistro: string;
}
