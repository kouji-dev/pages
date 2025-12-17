import {
  Component,
  ChangeDetectionStrategy,
  inject,
  computed,
  ViewContainerRef,
  TemplateRef,
  ViewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Button, Icon, Dropdown, Modal } from 'shared-ui';
import { OrganizationService } from '../../../../../application/services/organization.service';
import { CreateOrganizationModal } from '../../../../../features/organizations/components/create-organization-modal/create-organization-modal';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-sidebar-org-selector',
  imports: [CommonModule, Button, Icon, Dropdown, TranslatePipe],
  template: `
    <!-- Organization Selector Button -->
    <lib-button
      variant="ghost"
      size="md"
      [fullWidth]="true"
      [libDropdown]="orgDropdownTemplate"
      [position]="'below'"
      [attr.aria-expanded]="orgDropdown.open()"
      [attr.aria-label]="'organizations.selectOrganization' | translate"
      [disabled]="isLoading()"
      class="sidebar-org-selector_trigger"
      #orgDropdown="libDropdown"
    >
      <div class="sidebar-org-selector_content">
        <div class="sidebar-org-selector_icon">
          {{ orgInitials() }}
        </div>
        <span class="sidebar-org-selector_name">{{ orgName() }}</span>
        <lib-icon
          [name]="orgDropdown.open() ? 'chevron-up' : 'chevron-down'"
          size="xs"
          class="sidebar-org-selector_chevron"
        />
      </div>
    </lib-button>

    <!-- Organization Dropdown -->
    <ng-template #orgDropdownTemplate>
      <div class="sidebar-org-selector_dropdown">
        <div class="sidebar-org-selector_list">
          @for (org of organizations(); track org.id) {
            <lib-button
              variant="ghost"
              size="md"
              [fullWidth]="true"
              class="sidebar-org-selector_item"
              [class.sidebar-org-selector_item--active]="isCurrentOrganization(org.id)"
              (clicked)="selectOrganization(org.id, orgDropdown)"
            >
              <div class="sidebar-org-selector_item-icon">
                {{ getOrgInitials(org.name) }}
              </div>
              <div class="sidebar-org-selector_item-info">
                <div class="sidebar-org-selector_item-name">{{ org.name }}</div>
                @if (org.description) {
                  <div class="sidebar-org-selector_item-description">{{ org.description }}</div>
                }
              </div>
              @if (isCurrentOrganization(org.id)) {
                <lib-icon name="check" size="sm" class="sidebar-org-selector_item-check" />
              }
            </lib-button>
          }
        </div>
        <div class="sidebar-org-selector_divider"></div>
        <div class="sidebar-org-selector_actions">
          <lib-button
            variant="ghost"
            size="md"
            [fullWidth]="true"
            class="sidebar-org-selector_action"
            (clicked)="handleCreateOrganization(orgDropdown)"
          >
            <lib-icon name="plus" size="sm" class="sidebar-org-selector_action-icon" />
            <span>{{ 'organizations.createOrganization' | translate }}</span>
          </lib-button>
          @if (currentOrganization()) {
            <lib-button
              variant="ghost"
              size="md"
              [fullWidth]="true"
              class="sidebar-org-selector_action"
              (clicked)="handleGoToSettings(orgDropdown)"
            >
              <lib-icon name="settings" size="sm" class="sidebar-org-selector_action-icon" />
              <span>{{ 'organizations.settings' | translate }}</span>
            </lib-button>
          }
        </div>
      </div>
    </ng-template>
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        display: flex;
        @apply items-center;
        width: 100%;
        min-width: 0;
        height: 100%;
      }

      .sidebar-org-selector_trigger {
        width: 100%;
        min-width: 0;
        display: flex;
        @apply items-center justify-center;
        overflow: hidden;
        height: 100%;
      }

      .sidebar-org-selector_trigger .button {
        width: 100%;
        min-width: 0;
        overflow: hidden;
        height: 100%;
        display: flex;
        @apply items-center;
      }

      .sidebar-org-selector_trigger .button_content {
        @apply w-full;
        min-width: 0;
        @apply overflow-hidden;
        display: flex;
        @apply items-center;
      }

      .sidebar-org-selector_content {
        display: flex;
        @apply items-center;
        gap: 0.5rem;
        @apply w-full;
        min-width: 0;
        @apply overflow-hidden;
        height: 100%;
      }

      .sidebar-org-selector_icon {
        @apply h-8 w-8 rounded-lg bg-primary flex items-center justify-center flex-shrink-0;
        @apply text-primary-foreground font-semibold text-sm;
      }

      /* Compact mode adjustments */
      :host-context([data-density='compact']) .sidebar-org-selector_icon {
        @apply h-6 w-6;
        @apply text-xs;
      }

      .sidebar-org-selector_name {
        @apply font-semibold text-lg text-navigation-accent-foreground;
        @apply text-left;
        @apply min-w-0;
        @apply overflow-hidden;
        flex: 1 1 0;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      /* Compact mode adjustments */
      :host-context([data-density='compact']) .sidebar-org-selector_name {
        @apply text-base;
      }

      .sidebar-org-selector_chevron {
        @apply flex-shrink-0 text-muted-foreground;
      }

      .sidebar-org-selector_dropdown {
        @apply min-w-64;
      }

      .sidebar-org-selector_list {
        @apply flex flex-col;
        @apply py-1;
        max-height: 16rem;
        @apply overflow-y-auto;
      }

      .sidebar-org-selector_item {
        @apply justify-start;
        text-align: left;
      }

      .sidebar-org-selector_item .button {
        @apply justify-start;
        text-align: left;
      }

      .sidebar-org-selector_item--active {
        @apply bg-muted;
      }

      .sidebar-org-selector_item-icon {
        @apply h-6 w-6 rounded bg-primary/20 flex items-center justify-center flex-shrink-0;
        @apply text-primary font-medium text-xs;
      }

      .sidebar-org-selector_item-info {
        @apply flex flex-col;
        @apply flex-1;
        @apply min-w-0;
      }

      .sidebar-org-selector_item-name {
        @apply text-sm font-medium text-foreground;
      }

      .sidebar-org-selector_item-description {
        @apply text-xs text-muted-foreground truncate;
      }

      .sidebar-org-selector_item-check {
        @apply flex-shrink-0 text-primary;
      }

      .sidebar-org-selector_divider {
        @apply h-px bg-border;
      }

      .sidebar-org-selector_actions {
        @apply py-1;
        @apply flex flex-col;
        @apply gap-0;
      }

      .sidebar-org-selector_action {
        @apply justify-start text-primary;
      }

      .sidebar-org-selector_action .button {
        @apply justify-start text-primary;
      }

      .sidebar-org-selector_action-icon {
        @apply flex-shrink-0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class SidebarOrgSelector {
  private readonly organizationService = inject(OrganizationService);
  private readonly router = inject(Router);
  private readonly modal = inject(Modal);
  private readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(TranslateService);

  @ViewChild('orgDropdownTemplate') orgDropdownTemplate!: TemplateRef<any>;

  readonly isLoading = this.organizationService.isLoading;
  readonly currentOrganization = this.organizationService.currentOrganization;
  readonly organizations = this.organizationService.organizationsList;

  readonly orgName = computed(() => {
    const org = this.currentOrganization();
    return org?.name || this.translateService.instant('organizations.selectOrganization');
  });

  readonly orgInitials = computed(() => {
    const org = this.currentOrganization();
    if (!org?.name) return 'PD';
    return this.getOrgInitials(org.name);
  });

  getOrgInitials(name: string): string {
    const words = name.trim().split(/\s+/);
    if (words.length >= 2) {
      return (words[0][0] + words[words.length - 1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }

  isCurrentOrganization(organizationId: string): boolean {
    const current = this.currentOrganization();
    return current?.id === organizationId;
  }

  selectOrganization(organizationId: string, dropdown: Dropdown): void {
    this.organizationService.switchOrganization(organizationId);
    dropdown.open.set(false);
  }

  handleCreateOrganization(dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.modal.open(CreateOrganizationModal, this.viewContainerRef, {
      size: 'md',
      closable: true,
    });
  }

  handleGoToSettings(dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.router.navigate(['/app/organizations/settings']);
  }
}
