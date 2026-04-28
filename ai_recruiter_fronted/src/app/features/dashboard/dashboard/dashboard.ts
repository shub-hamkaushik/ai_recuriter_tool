import { Component, OnInit } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';
import { DashboardService } from '../../../core/services/dashboard';
import { NotificationService } from '../../../core/services/notification';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatButtonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  summaryCards = [
    { title: 'Total Candidates', value: 0, icon: 'people', color: 'primary' },
    { title: 'Active Jobs', value: 0, icon: 'work', color: 'accent' },
    { title: 'Resumes Uploaded', value: 0, icon: 'description', color: 'primary' },
    { title: 'Successful Matches', value: 0, icon: 'check_circle', color: 'tertiary' }
  ];

  recentActivities: Array<{ type: string; message: string; time: string }> = [];
  isLoading = false;

  constructor(
    private dashboardService: DashboardService,
    private notificationService: NotificationService
  ) {}

  ngOnInit() {
    this.loadDashboardData();
  }

  loadDashboardData() {
    this.isLoading = true;
    this.dashboardService.getDashboardSummary().subscribe({
      next: (data) => {
        this.summaryCards[0].value = data.totalCandidates;
        this.summaryCards[1].value = data.activeJobs;
        this.summaryCards[2].value = data.resumesUploaded;
        this.summaryCards[3].value = data.successfulMatches;
        this.recentActivities = [
          ...(data.recentResumes || []).map((item: any) => ({
            type: 'resume',
            message: `Resume uploaded: ${item.name}`,
            time: this.getTimeAgo(item.created_at),
          })),
          ...(data.recentJobs || []).map((item: any) => ({
            type: 'job',
          message: `Job created: ${item.title}`,
          time: this.getTimeAgo(item.created_at),
          })),
        ].slice(0, 8);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading dashboard data:', error);
        this.isLoading = false;
        this.notificationService.error('Unable to load dashboard data.');
      }
    });
  }

  private getTimeAgo(value: string): string {
    const date = new Date(value);
    const diffMs = Date.now() - date.getTime();
    const diffHours = Math.floor(diffMs / 3600000);
    if (diffHours < 1) {
      const diffMinutes = Math.max(1, Math.floor(diffMs / 60000));
      return `${diffMinutes} min ago`;
    }
    if (diffHours < 24) {
      return `${diffHours} hr ago`;
    }
    return `${Math.floor(diffHours / 24)} day ago`;
  }
}
