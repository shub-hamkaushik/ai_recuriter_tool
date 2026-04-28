import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDividerModule } from '@angular/material/divider';
import { CandidateService } from '../../../core/services/candidate';
import { MatchingService } from '../../../core/services/matching';
import { NotificationService } from '../../../core/services/notification';

interface MatchScore {
  jobId?: number;
  job: string;
  skillMatch: number;
  experienceMatch: number;
  overallScore: number;
  fitExplanation?: string;
  hiringRecommendation?: string;
}

@Component({
  selector: 'app-candidate-detail',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatChipsModule,
    MatIconModule,
    MatButtonModule,
    MatProgressBarModule,
    MatDividerModule
  ],
  templateUrl: './candidate-detail.html',
  styleUrls: ['./candidate-detail.css']
})
export class CandidateDetail implements OnInit {

  candidate: any = {};
  matchedJobs: MatchScore[] = [];
  isReprocessing = false;

  constructor(
    private route: ActivatedRoute,
    private candidateService: CandidateService,
    private matchingService: MatchingService,
    private notificationService: NotificationService
  ) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.params['id']);
    this.loadCandidate(id);
    this.loadMatchedJobs(id);
  }

  loadCandidate(id: number) {
    this.candidateService.getCandidate(id).subscribe({
      next: (candidate: any) => {
        this.candidate = {
          id: candidate.id,
          name: candidate.name,
          email: candidate.email,
          experienceYears: candidate.experience_years || 0,
          skills: candidate.parsed_skills || [],
          education: candidate.education_details || 'Not provided',
          experienceDescription: candidate.work_history_summary || 'No work history available.',
          summary: candidate.ai_summary || 'No AI summary generated yet.',
          resumeText: candidate.raw_resume_text || 'No resume text available.'
        };
      },
      error: (error) => {
        console.error('Error loading candidate:', error);
        this.notificationService.error('Unable to load candidate details.');
      }
    });
  }

  loadMatchedJobs(id: number) {
    this.matchingService.matchCandidateToJobs(id).subscribe({
      next: (matches: any[]) => {
        this.matchedJobs = matches.map((match) => ({
          jobId: match.job_id,
          job: match.job_title,
          skillMatch: match.skill_match_score,
          experienceMatch: match.experience_match_score,
          overallScore: match.overall_score,
          fitExplanation: match.fit_explanation,
          hiringRecommendation: match.hiring_recommendation,
        }));
        this.populateFitExplanations(id);
      },
      error: (error) => {
        console.error('Error loading matched jobs:', error);
        this.notificationService.error('Unable to load job matches for this candidate.');
      }
    });
  }

  getScoreColor(score: number): string {
    if (score >= 80) return '#22c55e'; // green
    if (score >= 50) return '#f59e0b'; // amber
    return '#ef4444'; // red
  }

  getScoreLabel(score: number): string {
    if (score >= 80) return 'Excellent Match';
    if (score >= 50) return 'Good Match';
    return 'Poor Match';
  }

  reprocessCandidate() {
    if (!this.candidate.id) {
      return;
    }
    this.isReprocessing = true;
    this.candidateService.reprocessCandidate(this.candidate.id).subscribe({
      next: (candidate) => {
        this.isReprocessing = false;
        this.candidate = {
          ...this.candidate,
          experienceYears: candidate.experience_years || 0,
          skills: candidate.parsed_skills || [],
          education: candidate.education_details || 'Not provided',
          experienceDescription: candidate.work_history_summary || 'No work history available.',
          summary: candidate.ai_summary || 'No AI summary generated yet.',
          resumeText: candidate.raw_resume_text || 'No resume text available.'
        };
        this.notificationService.success('Resume reprocessed successfully.');
      },
      error: (error) => {
        this.isReprocessing = false;
        console.error('Error reprocessing candidate:', error);
        this.notificationService.error('Resume reprocessing failed.');
      }
    });
  }

  private populateFitExplanations(candidateId: number) {
    this.matchedJobs
      .filter((match) => !match.fitExplanation && match.jobId)
      .slice(0, 3)
      .forEach((match) => {
        this.matchingService.generateFitExplanation(candidateId, match.jobId!).subscribe({
          next: (result) => {
            match.fitExplanation = result.fit_explanation;
            match.hiringRecommendation = result.hiring_recommendation;
            if (result.summary) {
              this.candidate.summary = result.summary;
            }
          },
          error: (error) => console.error('Error generating fit explanation:', error),
        });
      });
  }
}
