import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL, authHeaders } from './api-config';

@Injectable({
  providedIn: 'root'
})
export class SettingsService {
  private apiUrl = `${API_BASE_URL}/settings`;

  constructor(private http: HttpClient) {}

  getSettings(): Observable<any> {
    return this.http.get(`${this.apiUrl}/`, { headers: authHeaders() });
  }

  updateSettings(payload: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/`, payload, { headers: authHeaders() });
  }

  getAuditLogs(): Observable<any> {
    return this.http.get(`${this.apiUrl}/audit-logs`, { headers: authHeaders() });
  }
}
