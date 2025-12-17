import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  TemplateRef,
  ViewChild,
} from '@angular/core';
import {
  Icon,
  Dropdown,
  ListHeader,
  List,
  ListItemData,
  ListItemRow,
  ListItemIcon,
  ListItemLabel,
  ListItemActions,
  ListItemAction,
} from 'shared-ui';
import { AuthService } from '../../../core/auth/auth.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { ThemeService } from '../../../core/theme/theme.service';
import { DensityService } from '../../../core/services/density.service';
import { LanguageService, SupportedLanguage } from '../../../core/i18n/language.service';

@Component({
  selector: 'app-user-menu',
  imports: [
    Icon,
    Dropdown,
    TranslatePipe,
    ListHeader,
    List,
    ListItemRow,
    ListItemIcon,
    ListItemLabel,
    ListItemActions,
  ],
  template: `
    <div class="user-menu">
      <button
        class="user-menu_trigger"
        type="button"
        [libDropdown]="dropdownTemplate"
        [position]="'above'"
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
        <div class="user-menu_info">
          <span class="user-menu_name">{{ userName() }}</span>
          <span class="user-menu_email">{{ userEmail() }}</span>
        </div>
        <lib-icon
          [name]="dropdown.open() ? 'chevron-up' : 'chevron-down'"
          size="sm"
          class="user-menu_chevron"
        />
      </button>

      <ng-template #dropdownTemplate>
        <div class="user-menu_dropdown">
          <lib-list [items]="menuItems(dropdown)">
            <lib-list-header [title]="'userMenu.settings' | translate" />
          </lib-list>
        </div>
      </ng-template>

      <!-- Language Template -->
      <ng-template #languageTemplate let-item>
        <lib-list-item-row>
          <lib-list-item-icon name="globe" size="sm" />
          <lib-list-item-label>{{ 'language.language' | translate }}</lib-list-item-label>
          <lib-list-item-actions [actions]="languageActions()" />
        </lib-list-item-row>
      </ng-template>

      <!-- Theme Template -->
      <ng-template #themeTemplate let-item>
        <lib-list-item-row (click)="toggleTheme()">
          <lib-list-item-icon [name]="themeIcon()" size="sm" />
          <lib-list-item-label>{{ 'userMenu.theme' | translate }}</lib-list-item-label>
          <lib-list-item-actions [actions]="themeActions()" />
        </lib-list-item-row>
      </ng-template>

      <!-- Density Template -->
      <ng-template #densityTemplate let-item>
        <lib-list-item-row (click)="toggleDensity()">
          <lib-list-item-icon [name]="densityIcon()" size="sm" />
          <lib-list-item-label>{{ 'userMenu.density' | translate }}</lib-list-item-label>
          <lib-list-item-actions [actions]="densityActions()" />
        </lib-list-item-row>
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
        @apply flex items-center gap-2 w-full;
        @apply px-3 py-2;
        @apply rounded-md;
        @apply border-none bg-transparent;
        @apply transition-colors;
        @apply text-foreground;
        @apply cursor-pointer;
        @apply hover:bg-muted;
      }

      .user-menu_avatar {
        @apply w-8 h-8;
        @apply rounded-full;
        @apply overflow-hidden;
        @apply flex-shrink-0;
        @apply bg-muted;
      }

      .user-menu_avatar-image {
        @apply w-full h-full;
        @apply object-cover;
      }

      .user-menu_avatar-placeholder {
        @apply w-full h-full;
        @apply flex items-center justify-center;
        @apply text-xs font-semibold;
        @apply text-foreground;
      }

      .user-menu_info {
        @apply flex flex-col;
        @apply flex-1;
        @apply min-w-0;
        @apply hidden sm:flex;
      }

      .user-menu_name {
        @apply text-sm font-medium;
        @apply text-foreground;
        @apply truncate;
      }

      .user-menu_email {
        @apply text-xs;
        @apply text-muted-foreground;
        @apply truncate;
      }

      .user-menu_chevron {
        @apply flex-shrink-0;
        @apply hidden sm:block;
        @apply text-muted-foreground;
      }

      .user-menu_settings {
        @apply py-1;
      }

      .user-menu_settings ::ng-deep .list-header_title {
        @apply px-4 py-2;
      }

      .user-menu_setting {
        @apply flex items-center justify-between;
        @apply w-full;
        @apply px-4 py-2;
        @apply text-sm;
        @apply transition-colors;
        @apply text-foreground;
        @apply border-none bg-transparent;
        @apply cursor-pointer;
        @apply hover:bg-muted;
      }

      .user-menu_setting-info {
        @apply flex items-center gap-3;
        @apply flex-1;
        @apply min-w-0;
      }

      .user-menu_setting-icon {
        @apply flex-shrink-0;
        @apply text-muted-foreground;
      }

      .user-menu_setting-label {
        @apply text-foreground;
      }

      .user-menu_setting-option {
        min-width: 2.5rem;
        @apply text-center;
        @apply px-2;
        @apply text-xs;
      }

      .user-menu_setting-option ::ng-deep .button {
        @apply px-2 py-1;
        @apply text-xs;
        min-height: 1.75rem;
      }

      .user-menu_setting-value {
        @apply text-sm;
        @apply text-muted-foreground;
        @apply flex-shrink-0;
        @apply ml-auto;
      }

      .user-menu_dropdown ::ng-deep .list-item-row:hover .user-menu_setting-value {
        @apply text-foreground;
      }

      .user-menu_item {
        @apply flex items-center gap-3;
        @apply w-full;
        @apply px-4 py-2;
        @apply text-sm;
        @apply transition-colors;
        @apply text-foreground;
        text-decoration: none;
        @apply border-none bg-transparent;
        @apply cursor-pointer;
        @apply hover:bg-muted;
      }

      .user-menu_item-icon {
        @apply flex-shrink-0;
        @apply text-muted-foreground;
      }

      .user-menu_item--logout {
        @apply text-destructive;
      }

      .user-menu_item--logout:hover {
        @apply bg-destructive;
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
  private readonly themeService = inject(ThemeService);
  private readonly densityService = inject(DensityService);
  private readonly languageService = inject(LanguageService);
  private readonly translateService = inject(TranslateService);

  @ViewChild('dropdownTemplate') dropdownTemplate!: TemplateRef<any>;
  @ViewChild('languageTemplate') languageTemplate!: TemplateRef<any>;
  @ViewChild('themeTemplate') themeTemplate!: TemplateRef<any>;
  @ViewChild('densityTemplate') densityTemplate!: TemplateRef<any>;

  readonly currentUser = this.authService.currentUser;
  readonly currentLanguage = this.languageService.currentLanguage;
  readonly supportedLanguages = computed(() => this.languageService.getSupportedLanguages());

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

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }

  toggleDensity(): void {
    this.densityService.toggleDensity();
  }

  selectLanguage(lang: SupportedLanguage): void {
    this.languageService.setLanguage(lang);
  }

  readonly themeIcon = computed(() => {
    return this.themeService.theme() === 'dark' ? 'sun' : 'moon';
  });

  readonly themeLabel = computed(() => {
    return this.themeService.theme() === 'dark'
      ? this.translateService.instant('common.switchToLightMode')
      : this.translateService.instant('common.switchToDarkMode');
  });

  readonly densityIcon = computed(() => {
    return this.densityService.density() === 'compact' ? 'maximize-2' : 'minimize-2';
  });

  readonly densityLabel = computed(() => {
    return this.densityService.density() === 'compact'
      ? this.translateService.instant('common.switchToDefaultDensity') || 'Default'
      : this.translateService.instant('common.switchToCompactDensity') || 'Compact';
  });

  readonly languageActions = computed<ListItemAction[]>(() => {
    return this.supportedLanguages().map((lang) => ({
      label: lang.code.toUpperCase(),
      variant: lang.code === this.currentLanguage() ? 'primary' : 'ghost',
      size: 'sm' as const,
      onClick: () => this.selectLanguage(lang.code),
    }));
  });

  readonly themeActions = computed<ListItemAction[]>(() => [
    {
      label: this.themeLabel(),
      variant: 'ghost',
      size: 'sm',
    },
  ]);

  readonly densityActions = computed<ListItemAction[]>(() => [
    {
      label: this.densityLabel(),
      variant: 'ghost',
      size: 'sm',
    },
  ]);

  menuItems(dropdown: Dropdown): ListItemData[] {
    return [
      {
        id: 'profile',
        label: this.translateService.instant('navigation.profile'),
        icon: 'user',
        routerLink: ['/app/profile'],
        onClick: () => this.closeMenu(dropdown),
      },
      {
        id: 'settings',
        label: this.translateService.instant('navigation.settings'),
        icon: 'settings',
        routerLink: ['/settings'],
        onClick: () => this.closeMenu(dropdown),
      },
      {
        type: 'separator',
      },
      {
        id: 'language',
        label: this.translateService.instant('language.language'),
        icon: 'globe',
        itemTemplate: this.languageTemplate,
      },
      {
        id: 'theme',
        label: this.translateService.instant('userMenu.theme'),
        icon: this.themeIcon(),
        itemTemplate: this.themeTemplate,
      },
      {
        id: 'density',
        label: this.translateService.instant('userMenu.density'),
        icon: this.densityIcon(),
        itemTemplate: this.densityTemplate,
      },
      {
        type: 'separator',
      },
      {
        id: 'logout',
        label: this.translateService.instant('auth.logout'),
        icon: 'log-out',
        onClick: () => this.handleLogout(dropdown),
        variant: 'destructive',
      },
    ];
  }
}
