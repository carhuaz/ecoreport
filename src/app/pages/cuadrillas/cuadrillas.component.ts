import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReporteService } from '../../services/reporte.service';
import { CuadrillaService } from '../../services/cuadrilla.service';
import { Reporte } from '../../models/reporte.model';
import { Cuadrilla } from '../../models/cuadrilla.model';
import { BadgeEstadoComponent } from '../../shared/badge-estado/badge-estado.component';

interface ModalCuadrilla {
  abierto: boolean;
  editando: boolean;
  id?: number;
  nombre: string;
  responsable: string;
  distrito: string;
  zona_asignada: string;
}

@Component({
  selector: 'app-cuadrillas',
  standalone: true,
  imports: [CommonModule, FormsModule, BadgeEstadoComponent],
  templateUrl: './cuadrillas.component.html',
  styleUrls: ['./cuadrillas.component.css']
})
export class CuadrillasComponent implements OnInit {
  reportesAprobados: Reporte[] = [];
  cuadrillas: Cuadrilla[] = [];
  seleccion: { [reporteId: number]: number } = {};
  mensajeExito: string | null = null;
  mensajeError: string | null = null;

  modal: ModalCuadrilla = { abierto: false, editando: false, nombre: '', responsable: '', distrito: 'Huancayo', zona_asignada: '' };

  page = 1;
  pageSize = 10;
  total = 0;
  totalPages = 0;

  readonly pageSizes = [5, 10, 20, 50];

  get desde(): number { return (this.page - 1) * this.pageSize + 1; }
  get hasta(): number { return Math.min(this.page * this.pageSize, this.total); }

  constructor(
    private reporteService: ReporteService,
    private cuadrillaService: CuadrillaService
  ) {}

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.reporteService.obtenerReportes({ estado: 'Aprobado', page: this.page, page_size: this.pageSize }).subscribe(res => {
      this.reportesAprobados = res.items;
      this.total = res.total;
      this.totalPages = res.total_pages;
    });
    this.cuadrillaService.obtenerCuadrillas().subscribe(data => {
      this.cuadrillas = data;
    });
  }

  onPageSizeChange(): void {
    this.page = 1;
    this.cargar();
  }

  irPagina(p: number): void {
    if (p < 1 || p > this.totalPages) return;
    this.page = p;
    this.cargar();
  }

  paginaSiguiente(): void { this.irPagina(this.page + 1); }
  paginaAnterior(): void { this.irPagina(this.page - 1); }

  paginas(): number[] {
    const paginas: number[] = [];
    const inicio = Math.max(1, this.page - 2);
    const fin = Math.min(this.totalPages, this.page + 2);
    for (let i = inicio; i <= fin; i++) paginas.push(i);
    return paginas;
  }

  asignar(reporteId: number): void {
    const cuadrillaId = this.seleccion[reporteId];
    if (!cuadrillaId) return;
    this.cuadrillaService.asignarCuadrilla(reporteId, cuadrillaId).subscribe(() => {
      this.mensajeExito = 'Cuadrilla asignada correctamente';
      this.cargar();
      setTimeout(() => this.mensajeExito = null, 3000);
    });
  }

  abrirModalNueva(): void {
    this.modal = { abierto: true, editando: false, nombre: '', responsable: '', distrito: 'Huancayo', zona_asignada: '' };
  }

  abrirModalEditar(c: Cuadrilla): void {
    this.modal = {
      abierto: true, editando: true, id: c.id,
      nombre: c.nombre,
      responsable: c.responsable,
      distrito: c.distrito,
      zona_asignada: c.zonaAsignada || ''
    };
  }

  cerrarModal(): void {
    this.modal.abierto = false;
  }

  guardarCuadrilla(): void {
    this.mensajeError = null;
    if (!this.modal.nombre || !this.modal.responsable) {
      this.mensajeError = 'Nombre y responsable son obligatorios';
      return;
    }
    const data = {
      nombre: this.modal.nombre,
      responsable: this.modal.responsable,
      distrito: this.modal.distrito,
      zona_asignada: this.modal.zona_asignada
    };

    const action = this.modal.editando
      ? this.cuadrillaService.actualizarCuadrilla(this.modal.id!, data)
      : this.cuadrillaService.crearCuadrilla(data);

    action.subscribe(ok => {
      if (!ok) {
        this.mensajeError = 'Error al guardar la cuadrilla';
        return;
      }
      this.cerrarModal();
      this.mensajeExito = this.modal.editando ? 'Cuadrilla actualizada' : 'Cuadrilla creada';
      this.cargar();
      setTimeout(() => this.mensajeExito = null, 3000);
    });
  }

  eliminarCuadrilla(c: Cuadrilla): void {
    if (!confirm(`¿Eliminar "${c.nombre}"?`)) return;
    this.cuadrillaService.eliminarCuadrilla(c.id).subscribe(ok => {
      if (!ok) {
        this.mensajeError = 'No se puede eliminar: tiene reportes activos asignados';
        setTimeout(() => this.mensajeError = null, 4000);
        return;
      }
      this.mensajeExito = 'Cuadrilla eliminada';
      this.cargar();
      setTimeout(() => this.mensajeExito = null, 3000);
    });
  }
}
