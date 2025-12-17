import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  ViewContainerRef,
  effect,
} from '@angular/core';
import { Button, Icon, LoadingState, ErrorState, EmptyState, Modal } from 'shared-ui';
import { ToastService } from 'shared-ui';
import {
  OrganizationService,
  Organization,
} from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { DeleteOrganizationModal } from '../../components/delete-organization-modal/delete-organization-modal.component';
import { CreateOrganizationModal } from '../../components/create-organization-modal/create-organization-modal';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-organization-settings-page',
  imports: [Button, Icon, LoadingState, ErrorState, EmptyState, TranslatePipe],
  template: `
    <div class="org-settings-page">
      <div class="org-settings-page_header">
        <div class="org-settings-page_header-content">
          <div>
            <h1 class="org-settings-page_title">
              {{ 'organizations.settingsPage.title' | translate }}
            </h1>
            <p class="org-settings-page_subtitle">
              {{ 'organizations.settingsPage.subtitle' | translate }}
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

      <div class="org-settings-page_content">
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
          <div class="org-settings-page_list">
            @for (org of organizations(); track org.id) {
              <div class="org-settings-page_item">
                <div class="org-settings-page_item-content">
                  <div class="org-settings-page_item-icon">
                    {{ getOrgInitials(org.name) }}
                  </div>
                  <div class="org-settings-page_item-info">
                    <div class="org-settings-page_item-name">{{ org.name }}</div>
                    @if (org.description) {
                      <div class="org-settings-page_item-description">{{ org.description }}</div>
                    }
                    @if (org.slug) {
                      <div class="org-settings-page_item-slug">{{ org.slug }}</div>
                    }
                  </div>
                </div>
                <div class="org-settings-page_item-actions">
                  <lib-button
                    variant="ghost"
                    size="sm"
                    [iconOnly]="true"
                    (clicked)="handleEditOrganization(org)"
                    [attr.aria-label]="'organizations.editOrganization' | translate"
                  >
                    <lib-icon name="pencil" size="sm" />
                  </lib-button>
                  <lib-button
                    variant="ghost"
                    size="sm"
                    [iconOnly]="true"
                    (clicked)="handleDeleteOrganization(org)"
                    [attr.aria-label]="'organizations.deleteOrganization' | translate"
                  >
                    <lib-icon name="trash-2" size="sm" />
                  </lib-button>
                </div>
              </div>
            }
          </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .org-settings-page {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-background;
      }

      .org-settings-page_header {
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border;
      }

      .org-settings-page_header-content {
        @apply max-w-7xl mx-auto;
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .org-settings-page_title {
        @apply text-3xl font-bold mb-2;
        @apply text-foreground;
        margin: 0;
      }

      .org-settings-page_subtitle {
        @apply text-base;
        @apply text-muted-foreground;
        margin: 0;
      }

      .org-settings-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .org-settings-page_list {
        @apply max-w-7xl mx-auto;
        @apply flex flex-col;
        @apply gap-4;
      }

      .org-settings-page_item {
        @apply flex items-center justify-between;
        @apply p-4;
        @apply rounded-lg;
        @apply border;
        @apply border-border;
        @apply bg-background;
        @apply hover:bg-muted/50;
        @apply transition-colors;
        gap: 1rem;
      }

      .org-settings-page_item-content {
        @apply flex items-center;
        @apply flex-1;
        @apply min-w-0;
        gap: 1rem;
      }

      .org-settings-page_item-icon {
        @apply h-12 w-12 rounded-lg bg-primary flex items-center justify-center flex-shrink-0;
        @apply text-primary-foreground font-semibold text-base;
      }

      .org-settings-page_item-info {
        @apply flex flex-col;
        @apply flex-1;
        @apply min-w-0;
        gap: 0.25rem;
      }

      .org-settings-page_item-name {
        @apply text-base font-semibold text-foreground;
      }

      .org-settings-page_item-description {
        @apply text-sm text-muted-foreground;
      }

      .org-settings-page_item-slug {
        @apply text-xs text-muted-foreground;
        @apply font-mono;
      }

      .org-settings-page_item-actions {
        @apply flex items-center;
        gap: 0.5rem;
        flex-shrink: 0;
      }

      .org-settings-page_item-actions .button {
        @apply text-muted-foreground;
        @apply hover:text-foreground;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationSettingsPage {
  readonly organizationService = inject(OrganizationService);
  private readonly navigationService = inject(NavigationService);
  private readonly toast = inject(ToastService);
  private readonly modal = inject(Modal);
  private readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(TranslateService);

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

  private readonly initializeEffect = effect(() => {
    // Load organizations when component initializes
    this.organizationService.loadOrganizations();
  });

  getOrgInitials(name: string): string {
    const words = name.trim().split(/\s+/);
    if (words.length >= 2) {
      return (words[0][0] + words[words.length - 1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }

  handleCreateOrganization(): void {
    this.modal.open(CreateOrganizationModal, this.viewContainerRef, {
      size: 'md',
      closable: true,
    });
  }

  handleEditOrganization(organization: Organization): void {
    // TODO: Create EditOrganizationModal component
    // For now, navigate to the organization's projects page
    // In the future, we can open an edit modal
    this.navigationService.navigateToOrganizationProjects(organization.id);
  }

  handleDeleteOrganization(organization: Organization): void {
    this.modal
      .open<{ confirmed: boolean; organizationId?: string; error?: any }>(
        DeleteOrganizationModal,
        this.viewContainerRef,
        {
          size: 'md',
          data: {
            organization: organization,
          },
        },
      )
      .subscribe((result) => {
        if (result?.confirmed && result?.organizationId) {
          this.handleDeleteConfirm(result.organizationId);
        }
      });
  }

  async handleDeleteConfirm(organizationId: string): Promise<void> {
    try {
      await this.organizationService.deleteOrganization(organizationId);
      this.toast.success(this.translateService.instant('organizations.deleteSuccess'));
      // Reload organizations list
      await this.organizationService.loadOrganizations();
    } catch (error) {
      console.error('Failed to delete organization:', error);
      this.toast.error(this.translateService.instant('organizations.deleteError'));
    }
  }

  handleRetry(): void {
    this.organizationService.loadOrganizations();
  }
}
