import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CandidateService } from '../../../core/services/candidate';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';
import { MatTooltipModule } from '@angular/material/tooltip';
import { NotificationService } from '../../../core/services/notification';

export interface Candidate {
  id: number;
  name: string;
  email: string;
  experience: number;
  skills: string[];
  status: 'active' | 'inactive' | 'pending';
  matchScore?: number;
}

@Component({
  selector: 'app-candidate-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatInputModule,
    MatFormFieldModule,
    MatIconModule,
    MatButtonModule,
    MatChipsModule,
    MatCardModule,
    MatTooltipModule
  ],
  templateUrl: './candidate-list.html',
  styleUrls: ['./candidate-list.css']
})
export class CandidateList implements OnInit {

  constructor(
    private router: Router,
    private candidateService: CandidateService,
    private notificationService: NotificationService
  ) {}

  candidates: Candidate[] = [];
  filteredCandidates: Candidate[] = [];
  totalCandidates = 0;
  pageSize = 10;
  currentPage = 0;
  isLoading = false;

  searchText = '';
  selectedSkills: string[] = [];
  selectedExperience: string = '';
  selectedStatus: string = '';
  uploadName = '';
  uploadEmail = '';
  selectedResumeFile: File | null = null;
  isUploading = false;
  uploadMessage = '';
  uploadError = '';

  availableSkills = ['JavaScript', 'Python', 'Java', 'React', 'Angular', 'Node.js', 'SQL', 'AWS'];
  experienceLevels = ['1-2 years', '3-5 years', '5+ years'];

  displayedColumns: string[] = ['name', 'email', 'experience', 'skills', 'status', 'actions'];

  ngOnInit() {
    this.loadCandidates();
  }

  loadCandidates() {
    this.isLoading = true;
    this.candidateService.getCandidates(this.currentPage * this.pageSize, this.pageSize).subscribe({
      next: (response: any) => {
        const items = response.items || [];
        this.totalCandidates = response.total || items.length;
        this.candidates = items.map((c: any) => ({
          id: c.id,
          name: c.name,
          email: c.email,
          experience: c.experience_years || 0,
          skills: c.parsed_skills || [],
          status: (c.status || 'New').toLowerCase() === 'reviewed' ? 'active' : 'pending'
        }));
        this.applyFilters();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading candidates:', error);
        this.isLoading = false;
        this.candidates = [];
        this.filteredCandidates = [];
        this.notificationService.error('Unable to load candidates right now.');
      }
    });
  }

  onResumeFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    this.selectedResumeFile = input.files?.[0] || null;
    this.uploadMessage = '';
    this.uploadError = '';
  }

  uploadResume() {
    if (!this.uploadName.trim() || !this.uploadEmail.trim() || !this.selectedResumeFile) {
      this.uploadError = 'Enter candidate name, email, and select a PDF or TXT resume.';
      this.uploadMessage = '';
      return;
    }

    const formData = new FormData();
    formData.append('name', this.uploadName.trim());
    formData.append('email', this.uploadEmail.trim());
    formData.append('file', this.selectedResumeFile);

    this.isUploading = true;
    this.uploadError = '';
    this.uploadMessage = '';

    this.candidateService.uploadResume(formData).subscribe({
      next: () => {
        this.isUploading = false;
        this.uploadMessage = 'Resume uploaded successfully.';
        this.uploadName = '';
        this.uploadEmail = '';
        this.selectedResumeFile = null;
        this.loadCandidates();
        this.notificationService.success('Resume uploaded successfully.');
      },
      error: (error) => {
        console.error('Error uploading resume:', error);
        this.isUploading = false;
        this.uploadError = error?.error?.error || 'Resume upload failed.';
        this.notificationService.error(this.uploadError);
      }
    });
  }

  nextPage() {
    if ((this.currentPage + 1) * this.pageSize >= this.totalCandidates) {
      return;
    }
    this.currentPage += 1;
    this.loadCandidates();
  }

  prevPage() {
    if (this.currentPage === 0) {
      return;
    }
    this.currentPage -= 1;
    this.loadCandidates();
  }

  applyFilters() {
    this.filteredCandidates = this.candidates.filter(candidate => {
      const matchesSearch = candidate.name.toLowerCase().includes(this.searchText.toLowerCase()) ||
                           candidate.email.toLowerCase().includes(this.searchText.toLowerCase());

      const matchesSkills = this.selectedSkills.length === 0 ||
                           this.selectedSkills.some(skill => candidate.skills.includes(skill));

      const matchesExperience = !this.selectedExperience ||
                               this.getExperienceLevel(candidate.experience) === this.selectedExperience;

      const matchesStatus = !this.selectedStatus || candidate.status === this.selectedStatus;

      return matchesSearch && matchesSkills && matchesExperience && matchesStatus;
    });
  }

  getExperienceLevel(years: number): string {
    if (years <= 2) return '1-2 years';
    if (years <= 5) return '3-5 years';
    return '5+ years';
  }

  toggleSkillFilter(skill: string) {
    const index = this.selectedSkills.indexOf(skill);
    if (index > -1) {
      this.selectedSkills.splice(index, 1);
    } else {
      this.selectedSkills.push(skill);
    }
    this.applyFilters();
  }

  clearFilters() {
    this.searchText = '';
    this.selectedSkills = [];
    this.selectedExperience = '';
    this.selectedStatus = '';
    this.applyFilters();
  }

  goToDetail(id: number) {
    this.router.navigate(['/candidates', id]);
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'active': return 'tertiary';
      case 'pending': return 'accent';
      case 'inactive': return 'warn';
      default: return 'primary';
    }
  }
}
