import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL, authHeaders } from './api-config';

@Injectable({
  providedIn: 'root'
})
export class JobService {

  private apiUrl = `${API_BASE_URL}/jobs`;

  constructor(private http: HttpClient) {}

  getJobs(skip = 0, limit = 20): Observable<any> {
    return this.http.get(`${this.apiUrl}/?skip=${skip}&limit=${limit}`, { headers: authHeaders() });
  }

  createJob(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/`, data, { headers: authHeaders() });
  }

  getJob(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${id}`, { headers: authHeaders() });
  }

  updateJob(id: number, data: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}`, data, { headers: authHeaders() });
  }

  deleteJob(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`, { headers: authHeaders() });
  }

  enhanceJob(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/${id}/enhance`, {}, { headers: authHeaders() });
  }
}
