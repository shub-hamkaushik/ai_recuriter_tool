import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL, authHeaders } from './api-config';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = `${API_BASE_URL}/auth`;

  constructor(private http: HttpClient) {}

  login(credentials: { username: string; password: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, credentials);
  }

  register(userData: { username: string; email: string; password: string; role?: string }): Observable<any> {
    const headers = authHeaders();
    return this.http.post(`${this.apiUrl}/register`, userData, { headers });
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getCurrentUser(): any | null {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  }

  hasRole(...roles: string[]): boolean {
    const user = this.getCurrentUser();
    return !!user && roles.includes(user.role);
  }

  getUsers(): Observable<any> {
    return this.http.get(`${this.apiUrl}/users`, { headers: authHeaders() });
  }

  updateUser(userId: number, payload: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/users/${userId}`, payload, { headers: authHeaders() });
  }
}
