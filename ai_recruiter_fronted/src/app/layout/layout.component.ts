import { Component } from '@angular/core';
import { Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { RouterOutlet, Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, MatIconModule, MatButtonModule, MatMenuModule, MatTooltipModule, MatDividerModule, CommonModule],
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.css']
})
export class LayoutComponent {
  currentRoute = '';
  private readonly isBrowser: boolean;
  currentUser: any | null = null;

  navigationItems = [
    { label: 'Dashboard', route: '/dashboard', icon: 'dashboard', active: true },
    { label: 'Candidates', route: '/candidates', icon: 'people' },
    { label: 'Jobs', route: '/jobs', icon: 'work' },
    { label: 'Matching', route: '/matching', icon: 'analytics' }
  ];

  constructor(private router: Router, @Inject(PLATFORM_ID) platformId: object) {
    this.isBrowser = isPlatformBrowser(platformId);
    const user = this.isBrowser ? localStorage.getItem('user') : null;
    this.currentUser = user ? JSON.parse(user) : null;

    if (!user) {
      this.router.navigate(['/login']);
    }

    if (this.currentUser?.role === 'admin') {
      this.navigationItems.push(
        { label: 'Users', route: '/admin/users', icon: 'manage_accounts' },
        { label: 'Settings', route: '/admin/settings', icon: 'settings' },
      );
    }

    // Set active navigation based on current route
    this.router.events.subscribe(() => {
      this.currentRoute = this.router.url;
      this.updateActiveNavigation();
    });
  }

  navigateTo(route: string) {
    this.router.navigate([route]);
  }

  logout() {
    if (this.isBrowser) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }
    this.router.navigate(['/login']);
  }

  private updateActiveNavigation() {
    this.navigationItems.forEach(item => {
      item.active = this.currentRoute.startsWith(item.route);
    });
  }
}
