import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatStepperModule } from '@angular/material/stepper';
import { MatDividerModule } from '@angular/material/divider';
import { ActivatedRoute, Router } from '@angular/router';
import { JobService } from '../../../core/services/job';
import { NotificationService } from '../../../core/services/notification';

interface Skill {
  name: string;
}

@Component({
  selector: 'app-job-form',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatIconModule,
    MatCardModule,
    MatChipsModule,
    MatStepperModule,
    MatDividerModule
  ],
  templateUrl: './job-form.html',
  styleUrls: ['./job-form.css']
})
export class JobForm {
  jobForm: FormGroup;
  isSubmitting = false;
  currentSkill = '';
  formError = '';
  editingJobId: number | null = null;

  departments = [
    'Engineering',
    'Product',
    'Design',
    'Marketing',
    'Sales',
    'HR',
    'Finance',
    'Operations'
  ];

  employmentTypes = [
    'Full-time',
    'Part-time',
    'Contract',
    'Freelance',
    'Internship'
  ];

  experienceLevels = [
    'Entry Level (0-2 years)',
    'Mid Level (2-5 years)',
    'Senior Level (5-8 years)',
    'Lead/Principal (8+ years)',
    'Executive'
  ];

  skills: Skill[] = [];

  constructor(
    private fb: FormBuilder,
    public router: Router,
    private route: ActivatedRoute,
    private jobService: JobService,
    private notificationService: NotificationService,
  ) {
    this.jobForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      department: ['', Validators.required],
      employmentType: ['', Validators.required],
      experienceLevel: ['', Validators.required],
      location: [''],
      salaryRange: [''],
      description: ['', [Validators.required, Validators.minLength(10)]],
      requirements: [''],
      benefits: ['']
    });
    const routeId = Number(this.route.snapshot.params['id']);
    this.editingJobId = routeId || null;
    if (this.editingJobId) {
      this.loadJob(this.editingJobId);
    }
  }

  loadJob(jobId: number) {
    this.jobService.getJob(jobId).subscribe({
      next: (job) => {
        this.jobForm.patchValue({
          title: job.title,
          department: job.department,
          employmentType: job.employment_type || '',
          experienceLevel: this.getExperienceLabel(job.minimum_experience),
          location: job.location || '',
          description: job.description || '',
        });
        this.skills = (job.required_skills || []).map((name: string) => ({ name }));
      },
      error: (error) => {
        this.formError = 'Unable to load job for editing.';
        console.error('Error loading job:', error);
        this.notificationService.error(this.formError);
      },
    });
  }

  addSkill(event?: Event) {
    event?.preventDefault();
    event?.stopPropagation();

    if (this.currentSkill.trim() && !this.skills.find(s => s.name === this.currentSkill.trim())) {
      this.skills.push({ name: this.currentSkill.trim() });
      this.currentSkill = '';
    }
  }

  removeSkill(skill: Skill) {
    this.skills = this.skills.filter(s => s !== skill);
  }

  onSubmit() {
    this.formError = '';

    if (this.jobForm.invalid) {
      this.markFormGroupTouched();
      this.formError = this.getInvalidFormMessage();
      return;
    }

    this.isSubmitting = true;

    const jobData = {
      title: this.jobForm.value.title,
      department: this.jobForm.value.department,
      required_skills: this.skills.map(s => s.name),
      minimum_experience: this.getExperienceYears(this.jobForm.value.experienceLevel),
      description: [
        this.jobForm.value.description,
        this.jobForm.value.requirements ? `Requirements:\n${this.jobForm.value.requirements}` : '',
        this.jobForm.value.benefits ? `Benefits:\n${this.jobForm.value.benefits}` : '',
        this.jobForm.value.location ? `Location: ${this.jobForm.value.location}` : '',
        this.jobForm.value.salaryRange ? `Salary: ${this.jobForm.value.salaryRange}` : '',
        this.jobForm.value.employmentType ? `Employment Type: ${this.jobForm.value.employmentType}` : ''
      ].filter(Boolean).join('\n\n')
    };

    const request = this.editingJobId
      ? this.jobService.updateJob(this.editingJobId, jobData)
      : this.jobService.createJob(jobData);

    request.subscribe({
      next: (response) => {
        console.log('Job Created:', response);
        this.isSubmitting = false;
        this.notificationService.success(this.editingJobId ? 'Job updated successfully.' : 'Job created successfully.');
        this.router.navigate(['/jobs']);
      },
      error: (error) => {
        console.error('Error creating job:', error);
        this.isSubmitting = false;
        this.formError = error?.error?.error || 'Unable to create job. Please check your login and try again.';
        this.notificationService.error(this.formError);
      }
    });
  }

  private markFormGroupTouched() {
    Object.keys(this.jobForm.controls).forEach(key => {
      const control = this.jobForm.get(key);
      control?.markAsTouched();
    });
  }

  getFormProgress(): number {
    const controls = Object.keys(this.jobForm.controls);
    const validControls = controls.filter(key => this.jobForm.get(key)?.valid).length;
    return Math.round((validControls / controls.length) * 100);
  }

  getErrorMessage(controlName: string): string {
    const control = this.jobForm.get(controlName);
    if (!control) return '';
    if (control.hasError('required')) return 'This field is required';
    if (control.hasError('minlength')) {
      const requiredLength = control.getError('minlength').requiredLength;
      return `Please enter at least ${requiredLength} characters`;
    }
    return 'Please check this field';
  }

  private getInvalidFormMessage(): string {
    const missingLabels: Record<string, string> = {
      title: 'job title',
      department: 'department',
      employmentType: 'employment type',
      experienceLevel: 'experience level',
      description: 'job description'
    };

    const missing = Object.entries(missingLabels)
      .filter(([key]) => this.jobForm.get(key)?.invalid)
      .map(([, label]) => label);

    return missing.length
      ? `Please complete: ${missing.join(', ')}.`
      : 'Please check the highlighted fields.';
  }

  private getExperienceYears(experienceLevel: string): number {
    switch (experienceLevel) {
      case 'Entry Level (0-2 years)': return 1;
      case 'Mid Level (2-5 years)': return 3;
      case 'Senior Level (5-8 years)': return 6;
      case 'Lead/Principal (8+ years)': return 10;
      case 'Executive': return 15;
      default: return 1;
    }
  }

  private getExperienceLabel(minYears: number): string {
    if (minYears <= 1) return 'Entry Level (0-2 years)';
    if (minYears <= 3) return 'Mid Level (2-5 years)';
    if (minYears <= 6) return 'Senior Level (5-8 years)';
    if (minYears <= 10) return 'Lead/Principal (8+ years)';
    return 'Executive';
  }
}
