import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL, authHeaders } from './api-config';

@Injectable({
  providedIn: 'root'
})
export class MatchingService {

  private apiUrl = `${API_BASE_URL}/matching`;

  constructor(private http: HttpClient) {}

  matchCandidateToJobs(candidateId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/candidate/${candidateId}`, {}, { headers: authHeaders() });
  }

  matchJobToCandidates(jobId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/job/${jobId}`, {}, { headers: authHeaders() });
  }

  getRankedCandidatesForJob(jobId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/job/${jobId}`, { headers: authHeaders() });
  }

  getMatches(): Observable<any> {
    return this.http.get(`${this.apiUrl}/results`, { headers: authHeaders() });
  }

  generateFitExplanation(candidateId: number, jobId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/ai-summary/${candidateId}/${jobId}`, {}, { headers: authHeaders() });
  }
}
