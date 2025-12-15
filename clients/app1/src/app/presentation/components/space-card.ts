import { Component, ChangeDetectionStrategy, input, output, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Icon, Button } from 'shared-ui';
import { OrganizationService } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';
import { Space } from '../../application/services/space.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-space-card',
  imports: [Icon, RouterLink, Button, TranslatePipe],
  template: `
    <div class="space-card">
      <a
        [routerLink]="getSpaceRoute()"
        class="space-card_link"
        [attr.aria-label]="('spaces.viewSpace' | translate) + ': ' + space().name"
      >
        <div class="space-card_content">
          <div class="space-card_header">
            <div class="space-card_icon">
              <lib-icon name="book" size="lg" />
            </div>
          </div>
          <div class="space-card_info">
            <div class="space-card_title-row">
              <div class="space-card_key">{{ space().key }}</div>
              <h3 class="space-card_name">{{ space().name }}</h3>
            </div>
            @if (space().description) {
              <p class="space-card_description">{{ space().description }}</p>
            }
            <div class="space-card_meta">
              <div class="space-card_page-count">
                <lib-icon name="file-text" size="sm" />
                <span>{{ space().pageCount || 0 }} {{ 'spaces.pages' | translate }}</span>
              </div>
            </div>
          </div>
        </div>
      </a>
      <div class="space-card_actions">
        <lib-button
          variant="ghost"
          size="sm"
          [iconOnly]="true"
          leftIcon="settings"
          class="space-card_action-item"
          (clicked)="handleSettings()"
        >
        </lib-button>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .space-card {
        @apply relative;
        @apply flex flex-col;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-primary;
        @apply transition-all;
        @apply hover:shadow-lg;
        min-height: 180px;
      }

      .space-card_link {
        @apply flex-1;
        @apply p-6;
        text-decoration: none;
        color: inherit;
        @apply cursor-pointer;
        @apply transition-colors;
      }

      .space-card_link:hover {
        color: inherit;
      }

      .space-card_content {
        @apply flex flex-col;
        @apply gap-4;
      }

      .space-card_header {
        @apply flex items-center;
        @apply gap-3;
      }

      .space-card_icon {
        @apply flex items-center justify-center;
        @apply w-12 h-12;
        @apply rounded-lg;
        @apply bg-bg-tertiary;
        @apply text-primary-500;
      }

      .space-card_info {
        @apply flex flex-col;
        @apply gap-2;
        @apply flex-1;
      }

      .space-card_title-row {
        @apply flex items-center;
        @apply gap-2;
        @apply flex-wrap;
      }

      .space-card_key {
        @apply text-xs font-mono font-semibold;
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-bg-secondary;
        @apply text-text-secondary;
        @apply flex-shrink-0;
      }

      .space-card_name {
        @apply text-xl font-semibold;
        @apply text-text-primary;
        @apply flex-1;
        @apply min-w-0;
        margin: 0;
      }

      .space-card_description {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
        @apply line-clamp-2;
      }

      .space-card_meta {
        @apply flex items-center;
        @apply gap-4;
        @apply mt-auto;
      }

      .space-card_page-count {
        @apply flex items-center;
        @apply gap-2;
        @apply text-sm;
        @apply text-text-secondary;
      }

      .space-card_actions {
        @apply absolute;
        @apply top-4 right-4;
        @apply flex items-center;
        @apply gap-1;
        @apply z-10;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SpaceCard {
  private readonly organizationService = inject(OrganizationService);
  private readonly navigationService = inject(NavigationService);

  readonly space = input.required<Space>();
  readonly onSettings = output<Space>();

  getSpaceRoute(): string[] {
    const orgId = this.organizationService.currentOrganization()?.id;
    const spaceId = this.space().id;
    if (orgId) {
      return this.navigationService.getSpaceRoute(orgId, spaceId);
    }
    // Fallback if no org (shouldn't happen)
    return ['/app/organizations'];
  }

  handleSettings(): void {
    const orgId = this.organizationService.currentOrganization()?.id;
    const spaceId = this.space().id;
    if (orgId) {
      this.navigationService.navigateToSpaceSettings(orgId, spaceId);
    }
  }
}
