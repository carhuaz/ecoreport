export interface Cuadrilla {
  id: number;
  nombre: string;
  responsable: string;
  estado: 'Disponible' | 'En ruta' | 'Ocupada';
  zonaAsignada: string;
  distrito: string;
}
