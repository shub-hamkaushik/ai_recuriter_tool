import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatMenuModule } from '@angular/material/menu';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { FormsModule } from '@angular/forms';
import { JobService } from '../../../core/services/job';
import { NotificationService } from '../../../core/services/notification';

interface Job {
  id: number;
  title: string;
  department: string;
  experience: string;
  location: string;
  status: 'Open' | 'Closed' | 'Draft' | 'Paused';
  applicants: number;
  postedDate: Date;
  salary?: string;
  skills: string[];
  description: string;
}

@Component({
  selector: 'app-job-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatMenuModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDividerModule,
    MatTooltipModule
  ],
  templateUrl: './job-list.html',
  styleUrls: ['./job-list.css']
})
export class JobList implements OnInit {

  jobs: Job[] = [];
  filteredJobs: Job[] = [];
  currentView: 'grid' | 'list' = 'grid';
  searchQuery = '';
  selectedStatus = 'all';
  selectedJob: Job | null = null;
  isLoading = false;

  constructor(
    private router: Router,
    private jobService: JobService,
    private notificationService: NotificationService
  ) {}

  ngOnInit() {
    this.loadJobs();
  }

  loadJobs() {
    this.isLoading = true;
    this.jobService.getJobs().subscribe({
      next: (response: any) => {
        const data = response.items || [];
        this.jobs = data.map((job: any) => ({
          id: job.id,
          title: job.title,
          department: job.department || 'General',
          experience: this.getExperienceLevel(job.minimum_experience || 0),
          location: job.location || 'Remote',
          status: job.status || 'Open',
          applicants: 0,
          postedDate: job.created_at ? new Date(job.created_at) : new Date(),
          salary: undefined,
          skills: job.required_skills || [],
          description: job.description || ''
        }));
        this.filterJobs();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading jobs:', error);
        this.isLoading = false;
        this.jobs = [];
        this.filteredJobs = [];
        this.notificationService.error('Unable to load jobs right now.');
      }
    });
  }

  createJob() {
    this.router.navigate(['/jobs/create']);
  }

  selectJob(job: Job) {
    this.selectedJob = job;
  }

  viewJob(job: Job) {
    this.router.navigate(['/matching'], { queryParams: { jobId: job.id } });
  }

  editJob(job: Job) {
    this.router.navigate(['/jobs', job.id, 'edit']);
  }

  duplicateJob(job: Job) {
    const payload = {
      title: `${job.title} Copy`,
      department: job.department,
      required_skills: job.skills,
      minimum_experience: this.getMinimumExperience(job.experience),
      description: job.description
    };
    this.jobService.createJob(payload).subscribe({
      next: () => {
        this.notificationService.success(`Duplicated "${job.title}".`);
        this.loadJobs();
      },
      error: (error) => {
        console.error('Error duplicating job:', error);
        this.notificationService.error('Unable to duplicate this job.');
      }
    });
  }

  enhanceJob(job: Job) {
    this.jobService.enhanceJob(job.id).subscribe({
      next: () => {
        this.notificationService.success(`Enhanced "${job.title}" with AI.`);
        this.loadJobs();
      },
      error: (error) => {
        console.error('Error enhancing job:', error);
        this.notificationService.error('AI enhancement failed for this job.');
      },
    });
  }

  deleteJob(job: Job) {
    if (confirm(`Are you sure you want to delete "${job.title}"?`)) {
      this.jobService.deleteJob(job.id).subscribe({
        next: () => {
          this.notificationService.success(`Deleted "${job.title}".`);
          this.loadJobs();
        },
        error: (error) => {
          console.error('Error deleting job:', error);
          this.notificationService.error('Unable to delete this job.');
        }
      });
    }
  }

  toggleJobStatus(job: Job) {
    job.status = job.status === 'Open' ? 'Paused' : 'Open';
    this.jobService.updateJob(job.id, { status: job.status }).subscribe({
      next: () => {
        this.filterJobs();
        this.notificationService.success(`Job marked as ${job.status}.`);
      },
      error: (error) => {
        console.error('Error updating status:', error);
        this.notificationService.error('Unable to update job status.');
      },
    });
  }

  filterJobs() {
    this.filteredJobs = this.jobs.filter(job => {
      const search = this.searchQuery.toLowerCase();
      const matchesSearch = job.title.toLowerCase().includes(search) ||
        job.department.toLowerCase().includes(search);
      const matchesStatus = this.selectedStatus === 'all' ||
        job.status.toLowerCase() === this.selectedStatus;
      return matchesSearch && matchesStatus;
    });
  }

  onSearchChange() {
    this.filterJobs();
  }

  onStatusFilterChange() {
    this.filterJobs();
  }

  getExperienceLevel(years: number): string {
    if (years <= 2) return '1-2 years';
    if (years <= 5) return '3-5 years';
    return '5+ years';
  }

  getMinimumExperience(label: string): number {
    if (label === '1-2 years') return 1;
    if (label === '3-5 years') return 3;
    return 5;
  }

  getStatusColor(status: string): string {
    switch (status.toLowerCase()) {
      case 'open': return '#22c55e';
      case 'closed': return '#dc2626';
      case 'draft': return '#f59e0b';
      case 'paused': return '#6b7280';
      default: return '#6b7280';
    }
  }

  getStatusIcon(status: string): string {
    switch (status.toLowerCase()) {
      case 'open': return 'check_circle';
      case 'closed': return 'cancel';
      case 'draft': return 'edit';
      case 'paused': return 'pause';
      default: return 'help';
    }
  }

  get totalJobs(): number {
    return this.jobs.length;
  }

  get activeJobs(): number {
    return this.jobs.filter(j => j.status === 'Open').length;
  }

  get totalApplicants(): number {
    return this.jobs.reduce((sum, job) => sum + job.applicants, 0);
  }

  get jobsPostedThisWeek(): number {
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    return this.jobs.filter(j => new Date(j.postedDate) > oneWeekAgo).length;
  }

  getTimeAgo(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - new Date(date).getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return new Date(date).toLocaleDateString();
  }
}
