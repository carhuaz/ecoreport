import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReporteService } from '../../services/reporte.service';
import { Reporte } from '../../models/reporte.model';

interface Stat {
  label: string;
  valor: number;
  color: string;
  bg: string;
  porcentaje: number;
}

@Component({
  selector: 'app-estadisticas',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './estadisticas.component.html',
  styleUrls: ['./estadisticas.component.css']
})
export class EstadisticasComponent implements OnInit {
  reportes: Reporte[] = [];
  stats: Stat[] = [];

  get total() { return this.reportes.length; }

  constructor(private reporteService: ReporteService) {}

  ngOnInit(): void {
    this.reporteService.obtenerReportes({ page_size: 1000 }).subscribe(res => {
      this.reportes = res.items;
      this.calcularStats();
    });
  }

  calcularStats(): void {
    const estados: { label: string; estado: Reporte['estado']; color: string; bg: string }[] = [
      { label: 'Pendientes',  estado: 'Pendiente',  color: '#dc2626', bg: '#fee2e2' },
      { label: 'Aprobados',   estado: 'Aprobado',   color: '#2563eb', bg: '#dbeafe' },
      { label: 'Programados', estado: 'Programado', color: '#d97706', bg: '#fef3c7' },
      { label: 'Atendidos',   estado: 'Atendido',   color: '#16803c', bg: '#dcfce7' },
      { label: 'Rechazados',  estado: 'Rechazado',  color: '#6b7280', bg: '#f3f4f6' },
    ];

    this.stats = estados.map(e => {
      const valor = this.reportes.filter(r => r.estado === e.estado).length;
      return {
        label: e.label,
        valor,
        color: e.color,
        bg: e.bg,
        porcentaje: this.total > 0 ? Math.round((valor / this.total) * 100) : 0
      };
    });
  }
}
