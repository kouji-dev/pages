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
import { RouterLink } from '@angular/router';
import { Icon, Dropdown, Button, Modal } from 'shared-ui';
import { Organization } from '../../application/services/organization.service';

@Component({
  selector: 'app-organization-card',
  imports: [Icon, Dropdown, RouterLink, Button],
  template: `
    <div class="org-card">
      <a
        [routerLink]="['/organizations', organization().id]"
        class="org-card_link"
        [attr.aria-label]="'View ' + organization().name"
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
      </a>
      <div class="org-card_actions">
        <lib-button
          variant="ghost"
          size="sm"
          [iconOnly]="true"
          leftIcon="menu"
          [libDropdown]="actionsDropdownTemplate"
          [position]="'below'"
          class="org-card_actions-button"
          #actionsDropdown="libDropdown"
        >
        </lib-button>
        <ng-template #actionsDropdownTemplate>
          <div class="org-card_actions-menu">
            <lib-button
              variant="ghost"
              size="md"
              class="org-card_action-item"
              (clicked)="handleSettings(actionsDropdown)"
            >
              <lib-icon name="settings" size="sm" class="org-card_action-icon" />
              <span>Settings</span>
            </lib-button>
            <lib-button
              variant="ghost"
              size="md"
              class="org-card_action-item org-card_action-item--danger"
              (clicked)="handleLeave(actionsDropdown)"
            >
              <lib-icon name="log-out" size="sm" class="org-card_action-icon" />
              <span>Leave</span>
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
        @apply rounded-lg;
        @apply border;
        border-color: var(--color-border-default);
        background: var(--color-bg-primary);
        @apply transition-all;
        @apply hover:shadow-lg;
        min-height: 180px;
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
        background: var(--color-bg-tertiary);
        color: var(--color-primary-500);
      }

      .org-card_info {
        @apply flex flex-col;
        @apply gap-2;
        @apply flex-1;
      }

      .org-card_name {
        @apply text-xl font-semibold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .org-card_description {
        @apply text-sm;
        color: var(--color-text-secondary);
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
        color: var(--color-text-secondary);
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
        min-width: 10rem;
      }

      .org-card_action-item {
        @apply w-full;
        @apply justify-start;
        @apply px-4 py-2;
      }

      .org-card_action-icon {
        @apply flex-shrink-0;
      }

      .org-card_action-item--danger {
        color: var(--color-error);
      }

      .org-card_action-item--danger:hover {
        background: var(--color-error-50);
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationCard {
  readonly organization = input.required<Organization>();
  readonly onSettings = output<Organization>();
  readonly onLeave = output<Organization>();

  handleSettings(dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.onSettings.emit(this.organization());
  }

  handleLeave(dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.onLeave.emit(this.organization());
  }
}
