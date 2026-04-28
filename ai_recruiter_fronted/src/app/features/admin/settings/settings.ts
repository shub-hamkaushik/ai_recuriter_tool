import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { SettingsService } from '../../../core/services/settings';
import { NotificationService } from '../../../core/services/notification';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, MatCardModule, MatButtonModule, MatSlideToggleModule],
  templateUrl: './settings.html',
  styleUrls: ['./settings.css']
})
export class Settings implements OnInit {
  enableAiSummaries = true;
  enableFitExplanations = true;
  auditLogging = true;
  saved = false;
  auditLogs: any[] = [];
  isSaving = false;
  isLoadingLogs = false;

  constructor(
    private settingsService: SettingsService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.settingsService.getSettings().subscribe({
      next: (settings) => {
        this.enableAiSummaries = !!settings.enableAiSummaries;
        this.enableFitExplanations = !!settings.enableFitExplanations;
        this.auditLogging = !!settings.auditLogging;
      },
      error: (error) => {
        console.error('Error loading settings:', error);
        this.notificationService.error('Unable to load system settings.');
      },
    });

    this.loadAuditLogs();
  }

  saveSettings() {
    this.isSaving = true;
    this.saved = false;
    this.settingsService.updateSettings({
      enableAiSummaries: this.enableAiSummaries,
      enableFitExplanations: this.enableFitExplanations,
      auditLogging: this.auditLogging,
    }).subscribe({
      next: () => {
        this.isSaving = false;
        this.saved = true;
        this.notificationService.success('Settings saved successfully.');
        this.loadAuditLogs();
      },
      error: (error) => {
        console.error('Error saving settings:', error);
        this.isSaving = false;
        this.notificationService.error('Unable to save settings.');
      },
    });
  }

  loadAuditLogs() {
    this.isLoadingLogs = true;
    this.settingsService.getAuditLogs().subscribe({
      next: (logs) => {
        this.auditLogs = logs;
        this.isLoadingLogs = false;
      },
      error: (error) => {
        console.error('Error loading audit logs:', error);
        this.isLoadingLogs = false;
        this.notificationService.error('Unable to load audit logs.');
      },
    });
  }
}
