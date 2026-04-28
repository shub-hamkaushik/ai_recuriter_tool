import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL, authHeaders } from './api-config';

@Injectable({
  providedIn: 'root'
})
export class CandidateService {

  private apiUrl = `${API_BASE_URL}/candidates`;

  constructor(private http: HttpClient) {}

  getCandidates(skip = 0, limit = 10): Observable<any> {
    return this.http.get(`${this.apiUrl}/?skip=${skip}&limit=${limit}`, { headers: authHeaders() });
  }

  createCandidate(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/`, data, { headers: authHeaders() });
  }

  uploadResume(formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/upload`, formData, { headers: authHeaders() });
  }

  getCandidate(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${id}`, { headers: authHeaders() });
  }

  updateCandidate(id: number, data: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}`, data, { headers: authHeaders() });
  }

  reprocessCandidate(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/${id}/reprocess`, {}, { headers: authHeaders() });
  }

  deleteCandidate(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`, { headers: authHeaders() });
  }
}
