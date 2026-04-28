import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL, authHeaders } from './api-config';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {

  private dashboardUrl = `${API_BASE_URL}/dashboard/summary`;

  constructor(private http: HttpClient) {}

  getDashboardSummary(): Observable<any> {
    return this.http.get(this.dashboardUrl, { headers: authHeaders() });
  }
}
