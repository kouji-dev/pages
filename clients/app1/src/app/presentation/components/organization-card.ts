import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  computed,
  inject,
  TemplateRef,
  ViewChild,
  ViewContainerRef,
} from '@angular/core';
import { Icon, Dropdown, Button, Modal } from 'shared-ui';
import { Organization, OrganizationService } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';

@Component({
  selector: 'app-organization-card',
  imports: [Icon, Dropdown, Button],
  template: `
    <div class="org-card">
      <div
        class="org-card_link"
        [attr.aria-label]="'Switch to ' + organization().name"
        (click)="handleCardClick()"
      >
        <div class="org-card_content">
          <div class="org-card_icon">
            <lib-icon name="building" size="lg" />
          </div>
          <div class="org-card_info">
            <h3 class="org-card_name">{{ organization().name }}</h3>
            @if (organization().description) {
              <p class="org-card_description">{{ organization().description }}</p>
            }
            <div class="org-card_meta">
              <div class="org-card_member-count">
                <lib-icon name="users" size="sm" />
                <span>{{ organization().memberCount || 0 }} member(s)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="org-card_actions">
        <lib-button
          variant="ghost"
          size="sm"
          [iconOnly]="true"
          leftIcon="menu"
          [libDropdown]="actionsDropdownTemplate"
          [position]="'below'"
          [containerClass]="'lib-dropdown-panel--fit-content'"
          class="org-card_actions-button"
          #actionsDropdown="libDropdown"
        >
        </lib-button>
        <ng-template #actionsDropdownTemplate>
          <div class="org-card_actions-menu">
            <lib-button
              variant="ghost"
              size="md"
              [iconOnly]="true"
              leftIcon="settings"
              class="org-card_action-item"
              (clicked)="handleSettings(actionsDropdown)"
            >
            </lib-button>
            <lib-button
              variant="ghost"
              size="md"
              [iconOnly]="true"
              leftIcon="log-out"
              class="org-card_action-item org-card_action-item--danger"
              (clicked)="handleLeave(actionsDropdown)"
            >
            </lib-button>
          </div>
        </ng-template>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .org-card {
        @apply relative;
        @apply flex flex-col;
        @apply h-full;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-primary;
        @apply transition-all;
        @apply hover:shadow-lg;
      }

      .org-card_link {
        @apply flex-1;
        @apply p-6;
        text-decoration: none;
        color: inherit;
        @apply cursor-pointer;
        @apply transition-colors;
      }

      .org-card_link:hover {
        color: inherit;
      }

      .org-card_content {
        @apply flex flex-col;
        @apply gap-4;
      }

      .org-card_icon {
        @apply flex items-center justify-center;
        @apply w-12 h-12;
        @apply rounded-lg;
        @apply bg-bg-tertiary;
        @apply text-primary-500;
      }

      .org-card_info {
        @apply flex flex-col;
        @apply gap-2;
        @apply flex-1;
      }

      .org-card_name {
        @apply text-xl font-semibold;
        @apply text-text-primary;
        @apply truncate;
        margin: 0;
      }

      .org-card_description {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
        @apply line-clamp-2;
      }

      .org-card_meta {
        @apply flex items-center;
        @apply gap-4;
        @apply mt-auto;
      }

      .org-card_member-count {
        @apply flex items-center;
        @apply gap-2;
        @apply text-sm;
        @apply text-text-secondary;
      }

      .org-card_actions {
        @apply absolute;
        @apply top-4 right-4;
      }

      .org-card_actions-button {
        @apply z-10;
      }

      .org-card_actions-menu {
        @apply py-1;
        @apply flex flex-col;
        @apply gap-1;
      }

      .org-card_action-item--danger {
        @apply text-error;
      }

      .org-card_action-item--danger:hover {
        @apply bg-error-50;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationCard {
  private readonly organizationService = inject(OrganizationService);
  private readonly navigationService = inject(NavigationService);

  readonly organization = input.required<Organization>();
  readonly onSettings = output<Organization>();
  readonly onLeave = output<Organization>();

  handleCardClick(): void {
    const org = this.organization();
    const orgId = org.id;
    // Navigate to projects list for this organization
    // The organization resource will automatically load when URL changes
    this.navigationService.navigateToOrganizationProjects(orgId);
  }

  handleSettings(dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.onSettings.emit(this.organization());
  }

  handleLeave(dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.onLeave.emit(this.organization());
  }
}
