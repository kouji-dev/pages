import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  TemplateRef,
  ViewChild,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { Icon, Dropdown } from 'shared-ui';
import { AuthService } from '../../application/services/auth.service';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-user-menu',
  imports: [Icon, RouterLink, Dropdown, TranslatePipe],
  template: `
    <div class="user-menu">
      <button
        class="user-menu_trigger"
        type="button"
        [libDropdown]="dropdownTemplate"
        [position]="'below'"
        [attr.aria-expanded]="dropdown.open()"
        [attr.aria-label]="'userMenu.ariaLabel' | translate"
        #dropdown="libDropdown"
      >
        <div class="user-menu_avatar">
          @if (avatarUrl()) {
            <img [src]="avatarUrl()" [alt]="userName()" class="user-menu_avatar-image" />
          } @else {
            <div class="user-menu_avatar-placeholder">
              {{ initials() }}
            </div>
          }
        </div>
        <span class="user-menu_name">{{ userName() }}</span>
        <lib-icon
          [name]="dropdown.open() ? 'chevron-up' : 'chevron-down'"
          size="sm"
          class="user-menu_chevron"
        />
      </button>

      <ng-template #dropdownTemplate>
        <div class="user-menu_dropdown">
          <div class="user-menu_user-info">
            <div class="user-menu_user-info-avatar">
              @if (avatarUrl()) {
                <img
                  [src]="avatarUrl()"
                  [alt]="userName()"
                  class="user-menu_user-info-avatar-image"
                />
              } @else {
                <div class="user-menu_user-info-avatar-placeholder">
                  {{ initials() }}
                </div>
              }
            </div>
            <div class="user-menu_user-info-details">
              <div class="user-menu_user-info-name">{{ userName() }}</div>
              <div class="user-menu_user-info-email">{{ userEmail() }}</div>
            </div>
          </div>
          <div class="user-menu_divider"></div>
          <nav class="user-menu_nav">
            <a routerLink="/app/profile" class="user-menu_item" (click)="closeMenu(dropdown)">
              <lib-icon name="user" size="sm" class="user-menu_item-icon" />
              <span>{{ 'navigation.profile' | translate }}</span>
            </a>
            <a routerLink="/settings" class="user-menu_item" (click)="closeMenu(dropdown)">
              <lib-icon name="settings" size="sm" class="user-menu_item-icon" />
              <span>{{ 'navigation.settings' | translate }}</span>
            </a>
          </nav>
          <div class="user-menu_divider"></div>
          <div class="user-menu_actions">
            <button
              type="button"
              class="user-menu_item user-menu_item--logout"
              (click)="handleLogout(dropdown)"
            >
              <lib-icon name="log-out" size="sm" class="user-menu_item-icon" />
              <span>{{ 'auth.logout' | translate }}</span>
            </button>
          </div>
        </div>
      </ng-template>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .user-menu {
        @apply relative;
      }

      .user-menu_trigger {
        @apply flex items-center gap-2;
        @apply px-3 py-2;
        @apply rounded-md;
        @apply border-none bg-transparent;
        @apply transition-colors;
        @apply text-text-primary;
        @apply cursor-pointer;
        @apply hover:bg-gray-100;
      }

      .user-menu_avatar {
        @apply w-8 h-8;
        @apply rounded-full;
        @apply overflow-hidden;
        @apply flex-shrink-0;
        @apply bg-bg-tertiary;
      }

      .user-menu_avatar-image {
        @apply w-full h-full;
        @apply object-cover;
      }

      .user-menu_avatar-placeholder {
        @apply w-full h-full;
        @apply flex items-center justify-center;
        @apply text-xs font-semibold;
        @apply text-text-primary;
      }

      .user-menu_name {
        @apply text-sm font-medium;
        @apply hidden sm:inline;
        @apply text-text-primary;
      }

      .user-menu_chevron {
        @apply flex-shrink-0;
        @apply hidden sm:block;
        @apply text-text-secondary;
      }

      .user-menu_dropdown {
        @apply min-w-64;
        @apply overflow-hidden;
      }

      .user-menu_user-info {
        @apply flex items-center gap-3;
        @apply px-4 py-3;
        @apply bg-bg-secondary;
      }

      .user-menu_user-info-avatar {
        @apply w-10 h-10;
        @apply rounded-full;
        @apply overflow-hidden;
        @apply flex-shrink-0;
        @apply bg-bg-tertiary;
      }

      .user-menu_user-info-avatar-image {
        @apply w-full h-full;
        @apply object-cover;
      }

      .user-menu_user-info-avatar-placeholder {
        @apply w-full h-full;
        @apply flex items-center justify-center;
        @apply text-sm font-semibold;
        @apply text-text-primary;
      }

      .user-menu_user-info-details {
        @apply flex flex-col;
        @apply flex-1;
        @apply min-w-0;
      }

      .user-menu_user-info-name {
        @apply text-sm font-semibold;
        @apply text-text-primary;
        @apply truncate;
      }

      .user-menu_user-info-email {
        @apply text-xs;
        @apply text-text-secondary;
        @apply truncate;
      }

      .user-menu_divider {
        @apply h-px;
        @apply bg-border-default;
      }

      .user-menu_nav {
        @apply py-1;
      }

      .user-menu_actions {
        @apply py-1;
      }

      .user-menu_item {
        @apply flex items-center gap-3;
        @apply w-full;
        @apply px-4 py-2;
        @apply text-sm;
        @apply transition-colors;
        @apply text-text-primary;
        text-decoration: none;
        @apply border-none bg-transparent;
        @apply cursor-pointer;
        @apply hover:bg-gray-100;
      }

      .user-menu_item-icon {
        @apply flex-shrink-0;
        @apply text-text-secondary;
      }

      .user-menu_item--logout {
        @apply text-error;
      }

      .user-menu_item--logout:hover {
        @apply bg-error;
        color: white;
      }

      .user-menu_item--logout:hover .user-menu_item-icon {
        color: white;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserMenu {
  private readonly authService = inject(AuthService);

  @ViewChild('dropdownTemplate') dropdownTemplate!: TemplateRef<any>;

  readonly currentUser = this.authService.currentUser;

  readonly userName = computed(() => {
    const user = this.currentUser();
    return user?.name || 'User';
  });

  readonly userEmail = computed(() => {
    const user = this.currentUser();
    return user?.email || '';
  });

  readonly avatarUrl = computed(() => {
    const user = this.currentUser();
    return user?.avatarUrl;
  });

  readonly initials = computed(() => {
    const user = this.currentUser();
    if (!user) {
      return 'U';
    }
    const nameParts = user.name.split(' ');
    const initials = nameParts
      .map((part) => part.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
    return initials || 'U';
  });

  closeMenu(dropdown: Dropdown): void {
    dropdown.open.set(false);
  }

  handleLogout(dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.authService.logout();
  }
}
