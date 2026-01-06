import {
  Component,
  ChangeDetectionStrategy,
  signal,
  computed,
  inject,
  input,
  OnInit,
} from '@angular/core';
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
  AbstractControl,
  ValidationErrors,
  ValidatorFn,
} from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { Modal, ModalContainer, ModalHeader, ModalContent, ModalFooter } from 'shared-ui';
import { Button, Input } from 'shared-ui';
import { ToastService } from 'shared-ui';
import {
  SprintService,
  CreateSprintRequest,
} from '../../../../application/services/sprint.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-create-sprint-modal',
  imports: [
    ModalContainer,
    ModalHeader,
    ModalContent,
    ModalFooter,
    Button,
    Input,
    TranslatePipe,
    ReactiveFormsModule,
  ],
  template: `
    <lib-modal-container>
      <lib-modal-header>{{ 'sprints.modals.createSprint' | translate }}</lib-modal-header>
      <lib-modal-content>
        <form [formGroup]="form" class="create-sprint-form" (ngSubmit)="handleSubmit()">
          <lib-input
            [label]="'sprints.modals.sprintName' | translate"
            [placeholder]="'sprints.modals.sprintNamePlaceholder' | translate"
            [(model)]="name"
            [required]="true"
            [errorMessage]="nameError()"
            [helperText]="'sprints.modals.sprintNameHelper' | translate"
          />
          <lib-input
            [label]="'sprints.modals.startDate' | translate"
            type="date"
            [(model)]="startDate"
            [required]="true"
            [errorMessage]="startDateError()"
          />
          <lib-input
            [label]="'sprints.modals.endDate' | translate"
            type="date"
            [(model)]="endDate"
            [required]="true"
            [errorMessage]="endDateError()"
          />
          <lib-input
            [label]="'sprints.modals.sprintGoal' | translate"
            type="textarea"
            [placeholder]="'sprints.modals.sprintGoalPlaceholder' | translate"
            [(model)]="goal"
            [rows]="3"
            [helperText]="'sprints.modals.sprintGoalHelper' | translate"
          />
        </form>
      </lib-modal-content>
      <lib-modal-footer>
        <lib-button variant="secondary" (clicked)="handleCancel()" [disabled]="isSubmitting()">
          {{ 'common.cancel' | translate }}
        </lib-button>
        <lib-button
          variant="primary"
          (clicked)="handleSubmit()"
          [loading]="isSubmitting()"
          [disabled]="!form.valid || isSubmitting()"
        >
          {{ 'sprints.modals.createSprint' | translate }}
        </lib-button>
      </lib-modal-footer>
    </lib-modal-container>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .create-sprint-form {
        @apply flex flex-col gap-4;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CreateSprintModal implements OnInit {
  private readonly sprintService = inject(SprintService);
  private readonly toast = inject(ToastService);
  private readonly modal = inject(Modal);
  private readonly translateService = inject(TranslateService);
  private readonly navigationService = inject(NavigationService);

  readonly projectId = input<string | null>(null);

  // Form controls - validators set up at creation
  readonly form = this.createForm();

  // Signals for Input component binding (synced with form controls)
  readonly name = signal('');
  readonly startDate = signal('');
  readonly endDate = signal('');
  readonly goal = signal('');
  readonly isSubmitting = signal(false);

  readonly nameError = computed(() => {
    const control = this.form.get('name');
    if (control?.hasError('required') && control.touched) {
      return this.translateService.instant('sprints.modals.nameRequired');
    }
    if (control?.hasError('apiError')) {
      return control.getError('apiError');
    }
    return '';
  });

  readonly startDateError = computed(() => {
    const control = this.form.get('startDate');
    if (control?.hasError('required') && control.touched) {
      return this.translateService.instant('sprints.modals.startDateRequired');
    }
    if (control?.hasError('apiError')) {
      return control.getError('apiError');
    }
    return '';
  });

  readonly endDateError = computed(() => {
    const control = this.form.get('endDate');
    if (control?.hasError('required') && control.touched) {
      return this.translateService.instant('sprints.modals.endDateRequired');
    }
    if (control?.hasError('endDateBeforeStart')) {
      return this.translateService.instant('sprints.modals.endDateBeforeStart');
    }
    if (control?.hasError('apiError')) {
      return control.getError('apiError');
    }
    return '';
  });

  ngOnInit(): void {
    // Sync form controls with signals for Input component (one-way: form -> signals)
    this.setupFormValueSubscriptions();
  }

  /**
   * Create form with validators set up at creation
   */
  private createForm(): FormGroup {
    const form = new FormGroup(
      {
        name: new FormControl('', [Validators.required]),
        startDate: new FormControl('', [Validators.required]),
        endDate: new FormControl('', [Validators.required]),
        goal: new FormControl(''),
      },
      {
        validators: [this.createEndDateAfterStartValidator()],
      },
    );

    return form;
  }

  /**
   * Set up subscriptions to sync form controls with signals
   */
  private setupFormValueSubscriptions(): void {
    this.form.get('name')?.valueChanges.subscribe((value) => {
      this.name.set(value || '');
      // Clear API error when user changes the field
      this.clearApiError('name');
    });

    this.form.get('startDate')?.valueChanges.subscribe((value) => {
      this.startDate.set(value || '');
      // Clear API error when user changes the field
      this.clearApiError('startDate');
      // Update endDate validation when startDate changes
      this.form.get('endDate')?.updateValueAndValidity();
      this.form.updateValueAndValidity();
    });

    this.form.get('endDate')?.valueChanges.subscribe((value) => {
      this.endDate.set(value || '');
      // Clear API error when user changes the field
      this.clearApiError('endDate');
      // Update form-level validation when endDate changes
      this.form.updateValueAndValidity();
    });

    this.form.get('goal')?.valueChanges.subscribe((value) => {
      this.goal.set(value || '');
      // Clear API error when user changes the field
      this.clearApiError('goal');
    });
  }

  /**
   * Clear API error from a form field
   */
  private clearApiError(fieldName: string): void {
    const control = this.form.get(fieldName);
    if (control?.hasError('apiError')) {
      const errors = { ...control.errors };
      delete errors['apiError'];
      control.setErrors(Object.keys(errors).length > 0 ? errors : null);
    }
  }

  /**
   * Validator factory: End date must be after start date
   */
  private createEndDateAfterStartValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const formGroup = control as FormGroup;
      const startDate = formGroup.get('startDate')?.value;
      const endDate = formGroup.get('endDate')?.value;

      if (!endDate || !startDate) {
        return null;
      }

      const start = new Date(startDate);
      const end = new Date(endDate);

      if (end < start) {
        // Set error on endDate control
        formGroup.get('endDate')?.setErrors({ endDateBeforeStart: true });
        return { endDateBeforeStart: true };
      }

      // Clear the error if dates are valid
      const endDateControl = formGroup.get('endDate');
      if (endDateControl?.hasError('endDateBeforeStart')) {
        const errors = { ...endDateControl.errors };
        delete errors['endDateBeforeStart'];
        endDateControl.setErrors(Object.keys(errors).length > 0 ? errors : null);
      }

      return null;
    };
  }

  handleCancel(): void {
    this.modal.close();
  }

  async handleSubmit(): Promise<void> {
    // Mark all controls as touched to show validation errors
    this.form.markAllAsTouched();

    if (!this.form.valid) {
      return;
    }

    const projectId = this.projectId() || this.navigationService.currentProjectId();
    if (!projectId) {
      this.toast.error(this.translateService.instant('sprints.modals.noProjectSelected'));
      return;
    }

    this.isSubmitting.set(true);

    try {
      const formValue = this.form.value;
      const request: CreateSprintRequest = {
        name: (formValue.name || '').trim(),
        goal: (formValue.goal || '').trim() || undefined,
        startDate: formValue.startDate || '',
        endDate: formValue.endDate || '',
        projectId: projectId,
      };

      await this.sprintService.createSprint(request);

      this.toast.success(this.translateService.instant('sprints.modals.createSuccess'));
      this.modal.close();

      // Reset form
      this.form.reset();
      this.name.set('');
      this.startDate.set('');
      this.endDate.set('');
      this.goal.set('');

      // Sprint list will auto-reload via httpResource
    } catch (error) {
      console.error('Failed to create sprint:', error);
      this.handleApiError(error);
    } finally {
      this.isSubmitting.set(false);
    }
  }

  /**
   * Handle API errors and map them to form fields
   */
  private handleApiError(error: unknown): void {
    if (!(error instanceof HttpErrorResponse)) {
      this.toast.error(this.translateService.instant('sprints.modals.createError'));
      return;
    }

    const httpError = error as HttpErrorResponse;
    let hasFieldError = false;

    // Handle 422 validation errors (Pydantic field validation)
    if (httpError.status === 422) {
      // FastAPI default format: { detail: [{ loc: [...], msg: "...", type: "..." }] }
      // Custom handler format: { error: "...", message: "...", details: [{ field: "...", message: "...", type: "..." }] }
      const errorData = httpError.error;

      if (errorData?.detail && Array.isArray(errorData.detail)) {
        // FastAPI default RequestValidationError format
        for (const validationError of errorData.detail) {
          const field = this.mapApiFieldToFormField(validationError.loc);
          if (field) {
            this.setFieldError(field, validationError.msg || validationError.message);
            hasFieldError = true;
          }
        }
      } else if (errorData?.details && Array.isArray(errorData.details)) {
        // Custom validation error handler format
        for (const validationError of errorData.details) {
          // Extract field name from "body.name" format
          const fieldPath = validationError.field || '';
          const fieldName = fieldPath.split('.').pop() || '';
          const field = this.mapApiFieldToFormField([fieldName]);
          if (field) {
            this.setFieldError(field, validationError.message || validationError.msg);
            hasFieldError = true;
          }
        }
      }
    }

    // Handle 400, 409 errors (custom validation errors)
    if ((httpError.status === 400 || httpError.status === 409) && httpError.error?.detail) {
      const errorMessage = httpError.error.detail;

      // Map error messages to fields based on content
      if (this.isDateRangeError(errorMessage)) {
        this.setFieldError('endDate', errorMessage);
        hasFieldError = true;
      } else if (this.isOverlapError(errorMessage)) {
        this.setFieldError(
          'endDate',
          this.translateService.instant('sprints.modals.overlappingSprint'),
        );
        hasFieldError = true;
      } else if (this.isNameError(errorMessage)) {
        this.setFieldError('name', errorMessage);
        hasFieldError = true;
      }
    }

    // If no field-specific error was set, show generic error toast
    if (!hasFieldError) {
      const errorMessage =
        httpError.error?.detail ||
        httpError.error?.message ||
        this.translateService.instant('sprints.modals.createError');
      this.toast.error(errorMessage);
    }
  }

  /**
   * Map API field name to form field name
   * Handles FastAPI's RequestValidationError format where loc can be ["body", "field_name"]
   */
  private mapApiFieldToFormField(loc: string[] | unknown): string | null {
    if (!Array.isArray(loc) || loc.length === 0) {
      return null;
    }

    // FastAPI returns loc as ["body", "field_name"] or just ["field_name"]
    // Get the last element which is the actual field name
    const fieldName = loc[loc.length - 1];

    // Handle both string and number indices
    const fieldNameStr = String(fieldName);

    const fieldMap: Record<string, string> = {
      name: 'name',
      start_date: 'startDate',
      end_date: 'endDate',
      goal: 'goal',
    };

    return fieldMap[fieldNameStr] || null;
  }

  /**
   * Set error on a form field
   */
  private setFieldError(fieldName: string, errorMessage: string): void {
    const control = this.form.get(fieldName);
    if (control) {
      control.setErrors({ apiError: errorMessage });
      control.markAsTouched();
    }
  }

  /**
   * Check if error is related to date range
   */
  private isDateRangeError(message: string): boolean {
    const lowerMessage = message.toLowerCase();
    return (
      lowerMessage.includes('start date') ||
      lowerMessage.includes('end date') ||
      lowerMessage.includes('date must be') ||
      lowerMessage.includes('must be after')
    );
  }

  /**
   * Check if error is related to sprint overlap
   */
  private isOverlapError(message: string): boolean {
    const lowerMessage = message.toLowerCase();
    return lowerMessage.includes('overlap') || lowerMessage.includes('conflict');
  }

  /**
   * Check if error is related to name field
   */
  private isNameError(message: string): boolean {
    const lowerMessage = message.toLowerCase();
    return lowerMessage.includes('name') && !lowerMessage.includes('date');
  }
}
