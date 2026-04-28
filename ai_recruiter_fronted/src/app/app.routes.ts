import { Routes } from '@angular/router';
import { LayoutComponent } from './layout';
import { Dashboard } from './features/dashboard/dashboard/dashboard';
import { CandidateList } from './features/candidates/candidate-list/candidate-list';
import { CandidateDetail } from './features/candidates/candidate-detail/candidate-detail';
import { JobList } from './features/jobs/job-list/job-list';
import { JobForm } from './features/jobs/job-form/job-form';
import { Matching } from './features/matching/matching/matching';
import { Login } from './features/auth/login/login';
import { Register } from './features/auth/register/register';
import { authGuard } from './core/guards/auth.guard';
import { UserManagement } from './features/admin/user-management/user-management';
import { Settings } from './features/admin/settings/settings';

export const routes: Routes = [
    { path: '', redirectTo: 'login', pathMatch: 'full' },
    { path: 'login', component: Login },
    { path: 'register', component: Register },

  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: 'dashboard', component: Dashboard },
      { path: 'candidates', component: CandidateList },
      { path: 'candidates/:id', component: CandidateDetail },
      { path: 'jobs/create', component: JobForm },
      { path: 'jobs/:id/edit', component: JobForm },
      { path: 'jobs', component: JobList },
      { path: 'matching', component: Matching },
      { path: 'admin/users', component: UserManagement, canActivate: [authGuard], data: { roles: ['admin'] } },
      { path: 'admin/settings', component: Settings, canActivate: [authGuard], data: { roles: ['admin'] } },
    ]
  }
];
