import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JobForm } from './job-form';

describe('JobForm', () => {
  let component: JobForm;
  let fixture: ComponentFixture<JobForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JobForm],
    }).compileComponents();

    fixture = TestBed.createComponent(JobForm);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
