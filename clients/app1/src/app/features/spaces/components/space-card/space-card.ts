import { Component, ChangeDetectionStrategy, input, output, inject } from '@angular/core';
import { Icon, Button, Badge, Avatar, IconName, Dropdown } from 'shared-ui';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { Space } from '../../../../application/services/space.service';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-space-card',
  imports: [Icon, Button, Badge, Avatar, Dropdown, TranslatePipe],
  template: `
    <div class="space-card" (click)="handleCardClick()">
      <div class="space-card_content">
        <div class="space-card_header">
          <div class="space-card_icon-wrapper">
            <div class="space-card_icon">
              @if (space().icon && isEmoji(space().icon!)) {
                <span class="space-card_icon-emoji">{{ space().icon }}</span>
              } @else if (space().icon) {
                <lib-icon [name]="getIconName()" size="md" />
              } @else {
                <lib-icon name="book" size="md" />
              }
            </div>
            <div class="space-card_title-group">
              <h3 class="space-card_name">{{ space().name }}</h3>
              @if (space().status) {
                <lib-badge [variant]="getStatusVariant()" size="sm" class="space-card_status-badge">
                  {{ getStatusLabel() }}
                </lib-badge>
              }
            </div>
          </div>
          <lib-button
            variant="ghost"
            size="sm"
            [iconOnly]="true"
            leftIcon="ellipsis"
            class="space-card_more-button"
            [libDropdown]="cardActionsTemplate"
            [position]="'below'"
            #cardDropdown="libDropdown"
          >
          </lib-button>
          <ng-template #cardActionsTemplate>
            <div class="space-card_dropdown">
              <lib-button
                variant="ghost"
                size="sm"
                leftIcon="settings"
                [fullWidth]="true"
                class="space-card_dropdown-item"
                (clicked)="handleSettings(cardDropdown)"
              >
                {{ 'spaces.spaceSettings' | translate }}
              </lib-button>
              <lib-button
                variant="ghost"
                size="sm"
                leftIcon="trash"
                [fullWidth]="true"
                class="space-card_dropdown-item space-card_dropdown-item--danger"
                (clicked)="handleDelete(cardDropdown)"
              >
                {{ 'spaces.deleteSpace' | translate }}
              </lib-button>
            </div>
          </ng-template>
        </div>

        @if (space().description) {
          <p class="space-card_description">{{ space().description }}</p>
        }

        <div class="space-card_footer">
          <div class="space-card_owner">
            @if (space().owner) {
              <lib-avatar
                [avatarUrl]="space().owner!.avatar_url || undefined"
                [name]="space().owner!.name"
                [initials]="getInitials(space().owner!.name)"
                size="xs"
              />
              <span class="space-card_owner-name">{{ space().owner!.name }}</span>
            }
          </div>
          <div class="space-card_meta">
            @if (space().pageCount !== undefined) {
              <span class="space-card_meta-item">
                <lib-icon name="file-text" size="xs" />
                {{ space().pageCount }}
              </span>
            }
            @if (space().viewCount !== undefined) {
              <span class="space-card_meta-item">
                <lib-icon name="eye" size="xs" />
                {{ space().viewCount }}
              </span>
            }
            @if (space().lastUpdated) {
              <span class="space-card_meta-item">
                <lib-icon name="clock-4" size="xs" />
                {{ space().lastUpdated }}
              </span>
            }
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        display: contents;
      }

      .space-card {
        @apply relative;
        @apply flex flex-col;
        @apply rounded-lg;
        @apply border;
        @apply border-border;
        @apply bg-card;
        @apply transition-all;
        @apply hover:shadow-lg;
        @apply hover:scale-[1.02];
        @apply cursor-pointer;
        @apply h-full;
        @apply min-h-[160px];
      }

      .space-card_content {
        @apply flex flex-col;
        @apply gap-3;
        @apply h-full;
        @apply p-3;
      }

      .space-card_header {
        @apply flex items-start justify-between;
        @apply mb-2;
      }

      .space-card_icon-wrapper {
        @apply flex items-center gap-2;
        @apply flex-1;
        @apply min-w-0;
      }

      .space-card_icon {
        @apply h-8 w-8 rounded-lg bg-muted flex items-center justify-center;
        @apply flex-shrink-0;
      }

      .space-card_icon-emoji {
        @apply text-xl;
      }

      .space-card_title-group {
        @apply flex-1 min-w-0;
      }

      .space-card_name {
        @apply text-base font-semibold text-foreground;
        @apply hover:text-primary transition-colors;
        @apply truncate;
        margin: 0;
      }

      .space-card_status-badge {
        @apply mt-1;
      }

      .space-card_more-button {
        @apply h-8 w-8 opacity-0;
        @apply flex-shrink-0;
      }

      .space-card:hover .space-card_more-button {
        @apply opacity-100;
      }

      .space-card_dropdown {
        @apply flex flex-col;
        @apply py-1;
        @apply min-w-[160px];
      }

      .space-card_dropdown-item ::ng-deep .button {
        @apply justify-start;
      }

      .space-card_dropdown-item--danger ::ng-deep .button {
        @apply text-destructive;
      }

      .space-card_description {
        @apply text-sm text-muted-foreground;
        @apply overflow-hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        margin: 0;
      }

      .space-card_footer {
        @apply flex items-center justify-between;
        @apply mt-auto;
      }

      .space-card_owner {
        @apply flex items-center gap-2;
      }

      .space-card_owner-name {
        @apply text-sm text-muted-foreground;
        @apply truncate;
        max-width: 90px;
      }

      .space-card_meta {
        @apply flex items-center gap-2 text-xs text-muted-foreground;
      }

      .space-card_meta-item {
        @apply flex items-center gap-1;
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
  readonly onDelete = output<Space>();

  handleCardClick(): void {
    const orgId = this.organizationService.currentOrganization()?.id;
    const spaceId = this.space().id;
    if (orgId) {
      this.navigationService.navigateToSpace(orgId, spaceId);
    }
  }

  handleSettings(dropdown: Dropdown): void {
    dropdown.open.set(false);
    const orgId = this.organizationService.currentOrganization()?.id;
    const spaceId = this.space().id;
    if (orgId) {
      this.navigationService.navigateToSpaceSettings(orgId, spaceId);
    }
  }

  handleDelete(dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.onDelete.emit(this.space());
  }

  getStatusVariant(): 'default' | 'success' | 'warning' | 'danger' {
    const status = this.space().status;
    if (status === 'published') return 'success';
    if (status === 'in-review') return 'warning';
    if (status === 'draft') return 'default';
    return 'default';
  }

  getStatusLabel(): string {
    const status = this.space().status;
    const labels: Record<string, string> = {
      draft: 'Draft',
      'in-review': 'In Review',
      published: 'Published',
    };
    return labels[status || ''] || '';
  }

  isEmoji(str: string): boolean {
    return (
      str.length <= 2 && /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u.test(str)
    );
  }

  getIconName(): IconName {
    return (this.space().icon as IconName) || 'book';
  }

  getInitials(name: string): string {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  }
}
