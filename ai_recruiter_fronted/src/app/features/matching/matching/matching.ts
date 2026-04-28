import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { JobService } from '../../../core/services/job';
import { MatchingService } from '../../../core/services/matching';
import { NotificationService } from '../../../core/services/notification';

interface JobOption {
  id: number;
  title: string;
  description: string;
  skills: string[];
  minExp: number;
}

interface CandidateMatch {
  id: number;
  name: string;
  email: string;
  skills: string[];
  experience: number;
  skillMatch: number;
  experienceMatch: number;
  overallScore: number;
  status: 'excellent' | 'good' | 'poor';
}

@Component({
  selector: 'app-matching',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    MatCardModule,
    MatChipsModule,
    MatIconModule,
    MatButtonModule,
    MatProgressBarModule,
    MatTableModule,
    MatSortModule,
    MatFormFieldModule,
    MatSelectModule,
    MatTooltipModule
  ],
  templateUrl: './matching.html',
  styleUrls: ['./matching.css']
})
export class Matching implements OnInit {

  selectedJob: JobOption | null = null;
  jobs: JobOption[] = [];
  candidates: CandidateMatch[] = [];
  isLoading = false;
  displayedColumns: string[] = ['rank', 'name', 'skills', 'experience', 'skillMatch', 'experienceMatch', 'overallScore', 'actions'];

  constructor(
    private route: ActivatedRoute,
    private jobService: JobService,
    private matchingService: MatchingService,
    private notificationService: NotificationService
  ) {}

  ngOnInit() {
    this.loadJobs();
  }

  loadJobs() {
    this.isLoading = true;
    this.jobService.getJobs().subscribe({
      next: (response: any) => {
        const jobs = response.items || [];
        this.jobs = jobs.map((job: any) => ({
          id: job.id,
          title: job.title,
          description: job.enhanced_description || job.description || '',
          skills: job.required_skills || [],
          minExp: job.minimum_experience || 0
        }));

        const routeJobId = Number(this.route.snapshot.queryParamMap.get('jobId'));
        if (this.jobs.length > 0) {
          this.selectedJob = this.jobs.find((job) => job.id === routeJobId) || this.jobs[0];
          this.loadMatches();
        } else {
          this.isLoading = false;
        }
      },
      error: (error) => {
        console.error('Error loading jobs:', error);
        this.jobs = [];
        this.candidates = [];
        this.isLoading = false;
        this.notificationService.error('Unable to load jobs for matching.');
      }
    });
  }

  onJobChange() {
    this.loadMatches();
  }

  loadMatches() {
    if (!this.selectedJob?.id) {
      this.candidates = [];
      return;
    }

    this.matchingService.getRankedCandidatesForJob(this.selectedJob.id).subscribe({
      next: (matches: any[]) => {
        this.candidates = matches.map((match) => ({
          id: match.candidate_id,
          name: match.candidate_name,
          email: match.candidate_email,
          skills: match.overlapping_skills || [],
          experience: match.candidate_experience_years || 0,
          skillMatch: match.skill_match_score,
          experienceMatch: match.experience_match_score,
          overallScore: match.overall_score,
          status: this.getMatchStatus(match.overall_score)
        }));
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading matches:', error);
        this.candidates = [];
        this.isLoading = false;
        this.notificationService.error('Unable to load candidate rankings.');
      }
    });
  }

  getMatchStatus(score: number): 'excellent' | 'good' | 'poor' {
    if (score >= 80) return 'excellent';
    if (score >= 50) return 'good';
    return 'poor';
  }

  getScoreColor(score: number): string {
    if (score >= 80) return '#22c55e';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
  }
}
