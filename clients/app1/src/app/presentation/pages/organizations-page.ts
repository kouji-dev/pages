import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  ViewContainerRef,
  signal,
  effect,
} from '@angular/core';
import { Button, Icon, LoadingState, ErrorState, EmptyState, Modal } from 'shared-ui';
import { TranslatePipe } from '@ngx-translate/core';
import { OrganizationService, Organization } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';
import { OrganizationCard } from '../components/organization-card';
import { CreateOrganizationModal } from '../components/create-organization-modal';

@Component({
  selector: 'app-organizations-page',
  imports: [Button, LoadingState, ErrorState, EmptyState, OrganizationCard, TranslatePipe],
  template: `
    <div class="organizations-page">
      <div class="organizations-page_header">
        <div class="organizations-page_header-content">
          <div>
            <h1 class="organizations-page_title">{{ 'organizations.title' | translate }}</h1>
            <p class="organizations-page_subtitle">
              {{ 'organizations.subtitle' | translate }}
            </p>
          </div>
          <lib-button
            variant="primary"
            size="md"
            leftIcon="plus"
            (clicked)="handleCreateOrganization()"
          >
            {{ 'organizations.createOrganization' | translate }}
          </lib-button>
        </div>
      </div>

      <div class="organizations-page_content">
        @if (organizationService.isLoading()) {
          <lib-loading-state [message]="'organizations.loadingOrganizations' | translate" />
        } @else if (organizationService.hasError()) {
          <lib-error-state
            [title]="'organizations.failedToLoad' | translate"
            [message]="errorMessage()"
            [retryLabel]="'common.retry' | translate"
            (onRetry)="handleRetry()"
          />
        } @else if (organizations().length === 0) {
          <lib-empty-state
            [title]="'organizations.noOrganizations' | translate"
            [message]="'organizations.noOrganizationsDescription' | translate"
            icon="building"
            [actionLabel]="'organizations.createOrganization' | translate"
            actionIcon="plus"
            (onAction)="handleCreateOrganization()"
          />
        } @else {
          <div class="organizations-page_grid">
            @for (org of organizations(); track org.id) {
              <app-organization-card
                [organization]="org"
                (onSettings)="handleOrganizationSettings($event)"
                (onLeave)="handleOrganizationLeave($event)"
              />
            }
          </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .organizations-page {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-bg-primary;
      }

      .organizations-page_header {
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border-default;
      }

      .organizations-page_header-content {
        @apply max-w-7xl mx-auto;
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .organizations-page_title {
        @apply text-3xl font-bold;
        @apply text-text-primary;
        margin: 0 0 0.5rem 0;
      }

      .organizations-page_subtitle {
        @apply text-base;
        @apply text-text-secondary;
        margin: 0;
      }

      .organizations-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .organizations-page_grid {
        @apply max-w-7xl mx-auto;
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3;
        @apply gap-6;
        @apply items-stretch;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationsPage {
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);

  readonly organizations = computed(() => this.organizationService.organizationsList());

  readonly errorMessage = computed(() => {
    const error = this.organizationService.error();
    if (error) {
      return error instanceof Error
        ? error.message
        : 'An error occurred while loading organizations.';
    }
    return 'An unknown error occurred.';
  });

  private readonly initializeEffect = effect(
    () => {
      // Load organizations when component initializes
      this.organizationService.loadOrganizations();
    },
    { allowSignalWrites: true },
  );

  handleCreateOrganization(): void {
    this.modal.open(CreateOrganizationModal, this.viewContainerRef, {
      size: 'md',
    });
    // Note: CreateOrganizationModal already reloads organizations after creation
  }

  handleOrganizationSettings(organization: Organization): void {
    this.navigationService.navigateToOrganizationSettings(organization.id);
  }

  handleOrganizationLeave(organization: Organization): void {
    // TODO: Implement leave organization functionality (Task 1.2.14 or later)
    console.warn('Leave organization not yet implemented', organization);
  }

  handleRetry(): void {
    this.organizationService.loadOrganizations();
  }
}
