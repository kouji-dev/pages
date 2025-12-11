import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  TemplateRef,
  ViewChild,
  ViewContainerRef,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { Icon, Dropdown, Button, Modal } from 'shared-ui';
import { OrganizationService, Organization } from '../../application/services/organization.service';
import { CreateOrganizationModal } from './create-organization-modal';

@Component({
  selector: 'app-organization-selector',
  imports: [Icon, Dropdown, RouterLink, Button],
  template: `
    <div class="org-selector">
      <lib-button
        variant="ghost"
        size="md"
        [libDropdown]="dropdownTemplate"
        [position]="'below'"
        [attr.aria-expanded]="dropdown.open()"
        aria-label="Select organization"
        [disabled]="isLoading()"
        class="org-selector_trigger"
        #dropdown="libDropdown"
      >
        <div class="org-selector_current">
          <div class="org-selector_current-icon">
            <lib-icon name="building" size="sm" />
          </div>
          <div class="org-selector_current-info">
            <span class="org-selector_current-name">{{ currentOrgName() }}</span>
            @if (currentOrgDescription()) {
              <span class="org-selector_current-description">{{ currentOrgDescription() }}</span>
            }
          </div>
          <lib-icon
            [name]="dropdown.open() ? 'chevron-up' : 'chevron-down'"
            size="sm"
            class="org-selector_chevron"
          />
        </div>
      </lib-button>

      <ng-template #dropdownTemplate>
        <div class="org-selector_dropdown">
          <div class="org-selector_header">
            <div class="org-selector_header-title">Organizations</div>
            <a
              routerLink="/app/organizations"
              class="org-selector_header-link"
              (click)="closeMenu(dropdown)"
            >
              <lib-icon name="settings" size="sm" />
              <span>Manage</span>
            </a>
          </div>
          <div class="org-selector_divider"></div>
          <div class="org-selector_list">
            @for (org of organizations(); track org.id) {
              <lib-button
                variant="ghost"
                size="md"
                [fullWidth]="true"
                class="org-selector_item"
                [class.org-selector_item--active]="isCurrentOrganization(org.id)"
                (clicked)="selectOrganization(org.id, dropdown)"
              >
                <div class="org-selector_item-icon">
                  <lib-icon name="building" size="sm" />
                </div>
                <div class="org-selector_item-info">
                  <div class="org-selector_item-name">{{ org.name }}</div>
                  @if (org.description) {
                    <div class="org-selector_item-description">{{ org.description }}</div>
                  }
                </div>
                @if (isCurrentOrganization(org.id)) {
                  <lib-icon name="check" size="sm" class="org-selector_item-check" />
                }
              </lib-button>
            }
          </div>
          <div class="org-selector_divider"></div>
          <div class="org-selector_actions">
            <lib-button
              variant="ghost"
              size="md"
              [fullWidth]="true"
              class="org-selector_action"
              (clicked)="handleCreateOrganization(dropdown)"
            >
              <lib-icon name="plus" size="sm" class="org-selector_action-icon" />
              <span>Create Organization</span>
            </lib-button>
          </div>
        </div>
      </ng-template>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .org-selector {
        @apply relative;
      }

      .org-selector_trigger {
        min-width: 12rem;
        @apply w-full;
        @apply justify-start;
      }

      .org-selector_trigger .button {
        @apply w-full;
        @apply justify-start;
      }

      .org-selector_current {
        @apply flex items-center gap-2;
        @apply w-full;
      }

      .org-selector_current-icon {
        @apply flex-shrink-0;
        @apply text-text-secondary;
      }

      .org-selector_current-info {
        @apply flex flex-col;
        @apply flex-1;
        @apply min-w-0;
        @apply text-left;
      }

      .org-selector_current-name {
        @apply text-sm font-medium;
        @apply text-text-primary;
        @apply truncate;
      }

      .org-selector_current-description {
        @apply text-xs;
        @apply text-text-secondary;
        @apply truncate;
      }

      .org-selector_chevron {
        @apply flex-shrink-0;
        @apply text-text-secondary;
      }

      .org-selector_dropdown {
        @apply min-w-64;
      }

      .org-selector_header {
        @apply flex items-center justify-between;
        @apply px-4 py-3;
        @apply bg-bg-secondary;
      }

      .org-selector_header-title {
        @apply text-sm font-semibold;
        @apply text-text-primary;
      }

      .org-selector_header-link {
        @apply flex items-center gap-1.5;
        @apply text-xs;
        @apply text-primary-500;
        text-decoration: none;
        @apply transition-colors;
        @apply hover:opacity-80;
      }

      .org-selector_divider {
        @apply h-px;
        @apply bg-border-default;
      }

      .org-selector_list {
        @apply flex flex-col;
        @apply py-1;
        max-height: 16rem;
        @apply overflow-y-auto;
      }

      .org-selector_item {
        @apply justify-start;
        text-align: left;
      }

      .org-selector_item .button {
        @apply justify-start;
        text-align: left;
      }

      .org-selector_item .button_content {
        @apply flex items-center gap-3;
      }

      .org-selector_item--active {
        @apply bg-bg-secondary;
      }

      .org-selector_item-icon {
        @apply flex-shrink-0;
        @apply text-text-secondary;
      }

      .org-selector_item-info {
        @apply flex flex-col;
        @apply flex-1;
        @apply min-w-0;
      }

      .org-selector_item-name {
        @apply text-sm font-medium;
        @apply text-text-primary;
      }

      .org-selector_item-description {
        @apply text-xs;
        @apply text-text-secondary;
        @apply truncate;
      }

      .org-selector_item-check {
        @apply flex-shrink-0;
        @apply text-primary-500;
      }

      .org-selector_actions {
        @apply py-1;
      }

      .org-selector_action {
        @apply justify-start;
        @apply text-primary-500;
      }

      .org-selector_action .button {
        @apply justify-start;
        @apply text-primary-500;
      }

      .org-selector_action .button_content {
        @apply flex items-center gap-2;
      }

      .org-selector_action-icon {
        @apply flex-shrink-0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationSelector {
  private readonly organizationService = inject(OrganizationService);
  private readonly modal = inject(Modal);
  private readonly viewContainerRef = inject(ViewContainerRef);

  @ViewChild('dropdownTemplate') dropdownTemplate!: TemplateRef<any>;

  readonly isLoading = this.organizationService.isLoading;
  readonly currentOrganization = this.organizationService.currentOrganization;
  readonly organizations = this.organizationService.organizationsList;

  readonly currentOrgName = computed(() => {
    const org = this.currentOrganization();
    return org?.name || 'Select Organization';
  });

  readonly currentOrgDescription = computed(() => {
    const org = this.currentOrganization();
    return org?.description;
  });

  isCurrentOrganization(organizationId: string): boolean {
    const current = this.currentOrganization();
    return current?.id === organizationId;
  }

  selectOrganization(organizationId: string, dropdown: Dropdown): void {
    this.organizationService.switchOrganization(organizationId);
    dropdown.open.set(false);
    // TODO: Reload organization-specific data (projects, etc.)
    // TODO: Show toast notification
  }

  closeMenu(dropdown: Dropdown): void {
    dropdown.open.set(false);
  }

  handleCreateOrganization(dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.modal.open(CreateOrganizationModal, this.viewContainerRef, {
      size: 'md',
      closable: true,
    });
  }
}
