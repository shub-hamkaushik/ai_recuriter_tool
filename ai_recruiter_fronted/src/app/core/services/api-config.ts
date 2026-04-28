export const API_BASE_URL = 'http://127.0.0.1:5000';

export function authHeaders(): { [header: string]: string } {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}
