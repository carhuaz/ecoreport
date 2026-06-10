import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map } from 'rxjs/operators';
import { Reporte, EstadoReporte, PrioridadReporte, Distrito } from '../models/reporte.model';
import { Paginacion } from '../models/paginacion.model';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ReporteService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  private mapReporte(r: any): Reporte {
    const criterios = typeof r.criterios_prioridad === 'string'
      ? JSON.parse(r.criterios_prioridad) : (r.criterios_prioridad || []);
    const imagenes = typeof r.imagenes === 'string'
      ? JSON.parse(r.imagenes) : (r.imagenes || []);

    return {
      id: r.id,
      titulo: r.titulo,
      descripcion: r.descripcion,
      distrito: r.distrito,
      direccion: r.direccion,
      estado: r.estado,
      prioridad: r.prioridad,
      puntajePrioridad: r.puntaje_prioridad ?? r.puntajePrioridad,
      criteriosPrioridad: criterios,
      prioridadCorregida: !!r.prioridad_corregida,
      observacionPrioridad: r.observacion_prioridad,
      fecha: r.fecha || r.fecha_registro,
      latitud: r.latitud,
      longitud: r.longitud,
      imagenes,
      ciudadano: r.ciudadano || r.ciudadano_nombre,
      observacionValidacion: r.observacion_validacion,
      cuadrillaAsignada: r.cuadrilla_nombre || r.cuadrillaAsignada,
      historial: r.historial || []
    };
  }

  private paginada(url: string, params?: HttpParams): Observable<Paginacion<Reporte>> {
    return this.http.get<any>(url, { params }).pipe(
      map(res => ({
        ...res,
        items: res.items.map((r: any) => this.mapReporte(r))
      }))
    );
  }

  obtenerReportes(opts?: { page?: number; page_size?: number; estado?: string; distrito?: string; prioridad?: string }): Observable<Paginacion<Reporte>> {
    let params = new HttpParams();
    if (opts?.page) params = params.set('page', opts.page);
    if (opts?.page_size) params = params.set('page_size', opts.page_size);
    if (opts?.estado) params = params.set('estado', opts.estado);
    if (opts?.distrito) params = params.set('distrito', opts.distrito);
    if (opts?.prioridad) params = params.set('prioridad', opts.prioridad);
    return this.paginada(`${this.apiUrl}/reportes`, params);
  }

  obtenerReportesPublicos(opts?: { page?: number; page_size?: number; distrito?: string; estado?: string }): Observable<Paginacion<Reporte>> {
    let params = new HttpParams();
    if (opts?.page) params = params.set('page', opts.page);
    if (opts?.page_size) params = params.set('page_size', opts.page_size);
    if (opts?.distrito) params = params.set('distrito', opts.distrito);
    if (opts?.estado) params = params.set('estado', opts.estado);
    return this.paginada(`${this.apiUrl}/reportes/publicos`, params);
  }

  obtenerReportePorId(id: number): Observable<Reporte | undefined> {
    return this.http.get<any>(`${this.apiUrl}/reportes/${id}`).pipe(
      map(r => this.mapReporte(r))
    );
  }

  obtenerReportesPorEstado(estado: EstadoReporte, page = 1, page_size = 100): Observable<Paginacion<Reporte>> {
    return this.obtenerReportes({ estado, page, page_size });
  }

  obtenerReportesPorDistrito(distrito: Distrito, page = 1, page_size = 100): Observable<Paginacion<Reporte>> {
    return this.obtenerReportes({ distrito, page, page_size });
  }

  obtenerReportesPorCiudadano(_ciudadano: string, page = 1, page_size = 20): Observable<Paginacion<Reporte>> {
    let params = new HttpParams().set('page', page).set('page_size', page_size);
    return this.paginada(`${this.apiUrl}/reportes/mis-reportes`, params);
  }

  agregarReporte(reporte: any): Observable<Reporte> {
    const body = {
      titulo: reporte.titulo,
      descripcion: reporte.descripcion,
      distrito: reporte.distrito,
      direccion: reporte.direccion,
      latitud: reporte.latitud,
      longitud: reporte.longitud,
      imagenes: reporte.imagenes,
      prioridad: reporte.prioridad,
      puntaje_prioridad: reporte.puntajePrioridad || 0,
      criterios_prioridad: reporte.criteriosPrioridad || [],
      anonimo: reporte.anonimo || false
    };
    return this.http.post<any>(`${this.apiUrl}/reportes`, body).pipe(
      map(() => this.mapReporte({ ...reporte, ...body }))
    );
  }

  aprobarReporte(id: number, observacion: string, _validador: string): Observable<boolean> {
    return this.http.post(`${this.apiUrl}/reportes/${id}/aprobar`, { observacion }).pipe(
      map(() => true)
    );
  }

  rechazarReporte(id: number, observacion: string, _validador: string): Observable<boolean> {
    return this.http.post(`${this.apiUrl}/reportes/${id}/rechazar`, { observacion }).pipe(
      map(() => true)
    );
  }

  corregirPrioridad(id: number, prioridad: PrioridadReporte, observacion: string, _validador: string): Observable<boolean> {
    return this.http.post(`${this.apiUrl}/reportes/${id}/corregir-prioridad`, { prioridad, observacion }).pipe(
      map(() => true)
    );
  }

  asignarCuadrilla(id: number, _cuadrilla: string, _usuario: string): Observable<boolean> {
    return this.http.post(`${this.apiUrl}/reportes/${id}/asignar-cuadrilla`, { cuadrilla_id: +_cuadrilla }).pipe(
      map(() => true)
    );
  }

  marcarEnAtencion(id: number, _usuario: string): Observable<boolean> {
    return this.http.post(`${this.apiUrl}/reportes/${id}/atender`, {}).pipe(
      map(() => true)
    );
  }

  marcarAtendido(id: number, _usuario: string): Observable<boolean> {
    return this.http.post(`${this.apiUrl}/reportes/${id}/completar`, {}).pipe(
      map(() => true)
    );
  }

  marcarVerificado(id: number, _usuario: string): Observable<boolean> {
    return this.http.post(`${this.apiUrl}/reportes/${id}/verificar`, {}).pipe(
      map(() => true)
    );
  }

  obtenerResumenEstadisticas(): Observable<{ total_reportes: number; por_estado: { estado: string; cantidad: number }[]; por_distrito: { distrito: string; cantidad: number }[]; por_prioridad: { prioridad: string; cantidad: number }[] }> {
    return this.http.get<any>(`${this.apiUrl}/estadisticas/resumen`);
  }

  calcularPrioridadAsistida(respuestas: Record<string, boolean | number>): { prioridad: PrioridadReporte; puntaje: number; criterios: string[] } {
    let puntaje = 0;
    const criterios: string[] = [];

    if (respuestas['cantidad'] === 1) {
      puntaje += 1;
      criterios.push('Poca basura');
    } else if (respuestas['cantidad'] === 2) {
      puntaje += 2;
      criterios.push('Varias bolsas acumuladas');
    } else if (respuestas['cantidad'] === 3) {
      puntaje += 3;
      criterios.push('Gran acumulación de basura o desmonte');
    }

    if (respuestas['malosOlores']) { puntaje += 2; criterios.push('Malos olores'); }
    if (respuestas['animales']) { puntaje += 3; criterios.push('Presencia de animales, insectos o roedores'); }
    if (respuestas['cercania']) { puntaje += 3; criterios.push('Cercanía a viviendas, colegios, mercados, restaurantes o zonas concurridas'); }
    if (respuestas['agua']) { puntaje += 3; criterios.push('Cercanía a río, canal, acequia o área verde'); }
    if (respuestas['bloqueo']) { puntaje += 3; criterios.push('Bloqueo de vereda, pista o zona de tránsito'); }
    if (respuestas['peligroso']) { puntaje += 4; criterios.push('Residuos peligrosos o sospechosos'); }
    if (respuestas['imagenClara']) { puntaje += 1; criterios.push('Imagen clara como evidencia'); }

    let prioridad: PrioridadReporte = 'Baja';
    if (puntaje >= 12) prioridad = 'Crítica';
    else if (puntaje >= 8) prioridad = 'Alta';
    else if (puntaje >= 4) prioridad = 'Media';

    return { prioridad, puntaje, criterios };
  }
}
