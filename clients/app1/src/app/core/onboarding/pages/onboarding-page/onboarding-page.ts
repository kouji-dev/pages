import {
  Component,
  ChangeDetectionStrategy,
  inject,
  effect,
  signal,
  computed,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Button, Icon, Input, ToastService } from 'shared-ui';
import { OnboardingService } from '../../onboarding.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-onboarding-page',
  imports: [CommonModule, Button, Icon, Input, TranslatePipe],
  template: `
    <div class="onboarding-page">
      <div class="onboarding-page_container">
        <div class="onboarding-page_header">
          <div class="onboarding-page_icon">
            <lib-icon name="rocket" size="lg" />
          </div>
          <h1 class="onboarding-page_title">{{ 'onboarding.title' | translate }}</h1>
          <p class="onboarding-page_description">
            {{ 'onboarding.description' | translate }}
          </p>
        </div>

        <div class="onboarding-page_content">
          <div class="onboarding-page_step">
            <div class="onboarding-page_step-header">
              <div class="onboarding-page_step-number">1</div>
              <div class="onboarding-page_step-info">
                <h2 class="onboarding-page_step-title">
                  {{ 'onboarding.step.title' | translate }}
                </h2>
                <p class="onboarding-page_step-description">
                  {{ 'onboarding.step.description' | translate }}
                </p>
              </div>
            </div>
            <div class="onboarding-page_step-content">
              <form class="onboarding-page_form" (ngSubmit)="handleSubmit()">
                <lib-input
                  [label]="'organizations.modals.organizationName' | translate"
                  [placeholder]="'organizations.modals.organizationNamePlaceholder' | translate"
                  [(model)]="name"
                  [required]="true"
                  [errorMessage]="nameError()"
                  [helperText]="'organizations.modals.organizationNameHelper' | translate"
                />
                <lib-input
                  [label]="'organizations.modals.slug' | translate"
                  [placeholder]="'organizations.modals.slugPlaceholder' | translate"
                  [(model)]="slug"
                  [required]="true"
                  [errorMessage]="slugError()"
                  [helperText]="'organizations.modals.slugHelper' | translate"
                />
                <lib-input
                  [label]="'organizations.modals.description' | translate"
                  type="textarea"
                  [placeholder]="'organizations.modals.descriptionPlaceholder' | translate"
                  [(model)]="description"
                  [rows]="3"
                  [helperText]="'organizations.modals.descriptionHelper' | translate"
                />
                <div class="onboarding-page_form-actions">
                  <lib-button
                    variant="primary"
                    size="lg"
                    type="submit"
                    [loading]="isSubmitting()"
                    [disabled]="!isValid()"
                  >
                    <lib-icon name="plus" size="sm" />
                    {{ 'onboarding.createButton' | translate }}
                  </lib-button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .onboarding-page {
        @apply min-h-screen;
        @apply flex items-center justify-center;
        @apply bg-muted/30;
        @apply p-6;
      }

      .onboarding-page_container {
        @apply w-full max-w-2xl;
        @apply bg-card rounded-lg shadow-lg border border-border;
        @apply p-8;
      }

      .onboarding-page_header {
        @apply text-center mb-8;
      }

      .onboarding-page_icon {
        @apply h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4;
        @apply text-primary;
      }

      .onboarding-page_title {
        @apply text-3xl font-semibold text-foreground mb-3;
      }

      .onboarding-page_description {
        @apply text-muted-foreground text-lg;
        @apply leading-relaxed;
      }

      .onboarding-page_content {
        @apply space-y-6;
      }

      .onboarding-page_step {
        @apply p-6 rounded-lg bg-muted/50;
        @apply border border-border;
      }

      .onboarding-page_step-header {
        @apply flex items-start gap-4 mb-6;
      }

      .onboarding-page_step-number {
        @apply h-10 w-10 rounded-full bg-primary flex items-center justify-center flex-shrink-0;
        @apply text-primary-foreground font-bold text-lg;
      }

      .onboarding-page_step-info {
        @apply flex-1;
      }

      .onboarding-page_step-title {
        @apply text-xl font-semibold text-foreground mb-2;
      }

      .onboarding-page_step-description {
        @apply text-muted-foreground;
        @apply leading-relaxed;
      }

      .onboarding-page_step-content {
        @apply mt-6;
      }

      .onboarding-page_form {
        @apply flex flex-col gap-4;
      }

      .onboarding-page_form-actions {
        @apply flex justify-center mt-6;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class OnboardingPage {
  private readonly router = inject(Router);
  private readonly onboardingService = inject(OnboardingService);
  private readonly organizationService = inject(OrganizationService);
  private readonly toast = inject(ToastService);
  private readonly translateService = inject(TranslateService);

  readonly name = signal('');
  readonly slug = signal('');
  readonly description = signal('');
  readonly isSubmitting = signal(false);

  readonly nameError = computed(() => {
    const value = this.name();
    if (!value.trim()) {
      return this.translateService.instant('organizations.modals.nameRequired');
    }
    if (value.trim().length < 3) {
      return this.translateService.instant('organizations.modals.nameMinLength');
    }
    return '';
  });

  readonly slugError = computed(() => {
    const value = this.slug();
    if (!value.trim()) {
      return this.translateService.instant('organizations.modals.slugRequired');
    }
    // Slug format validation: lowercase, letters, numbers, hyphens only
    const slugPattern = /^[a-z0-9-]+$/;
    if (!slugPattern.test(value)) {
      return this.translateService.instant('organizations.modals.slugInvalidFormat');
    }
    if (value.length < 3) {
      return this.translateService.instant('organizations.modals.slugMinLength');
    }
    return '';
  });

  readonly isValid = computed(() => {
    return !this.nameError() && !this.slugError() && this.name().trim() && this.slug().trim();
  });

  private readonly lastAutoGeneratedSlug = signal<string>('');
  private readonly slugManuallyEdited = signal(false);

  constructor() {
    // Auto-generate slug when name changes (only if not manually edited)
    effect(() => {
      const nameValue = this.name();
      if (!nameValue || this.slugManuallyEdited()) {
        return;
      }

      const newSlug = this.generateSlug(nameValue);
      this.slug.set(newSlug);
      this.lastAutoGeneratedSlug.set(newSlug);
    });

    // Track when slug is manually edited
    effect(() => {
      const slugValue = this.slug();
      const lastAutoSlug = this.lastAutoGeneratedSlug();
      // If slug differs from last auto-generated, mark as manually edited
      if (slugValue && lastAutoSlug && slugValue !== lastAutoSlug) {
        this.slugManuallyEdited.set(true);
      }
    });

    // Watch for organization creation to complete onboarding
    effect(() => {
      const orgs = this.organizationService.organizationsList();
      if (orgs.length > 0) {
        this.onboardingService.completeOnboarding();
        // Navigate to the new organization
        if (orgs[0]) {
          this.router.navigate(['/app/organizations', orgs[0].id, 'dashboard']);
        }
      }
    });
  }

  /**
   * Auto-generate slug from organization name
   */
  private generateSlug(name: string): string {
    return name
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9\s-]/g, '') // Remove special characters
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .replace(/-+/g, '-') // Replace multiple hyphens with single hyphen
      .replace(/^-|-$/g, ''); // Remove leading/trailing hyphens
  }

  async handleSubmit(): Promise<void> {
    if (!this.isValid()) {
      return;
    }

    this.isSubmitting.set(true);

    try {
      const newOrg = await this.organizationService.createOrganization({
        name: this.name().trim(),
        slug: this.slug().trim(),
        description: this.description().trim() || undefined,
      });

      this.toast.success(this.translateService.instant('organizations.modals.createSuccess'));

      // Reset form
      this.name.set('');
      this.slug.set('');
      this.description.set('');
      this.lastAutoGeneratedSlug.set('');
      this.slugManuallyEdited.set(false);

      // Refresh organizations list and switch to new organization
      this.organizationService.loadOrganizations();
      if (newOrg) {
        // Wait a bit for loadOrganizations to complete before switching
        setTimeout(() => {
          this.organizationService.switchOrganization(newOrg.id);
        }, 500);
      }
    } catch (error) {
      console.error('Failed to create organization:', error);
      this.toast.error(this.translateService.instant('organizations.modals.createError'));
    } finally {
      this.isSubmitting.set(false);
    }
  }
}
