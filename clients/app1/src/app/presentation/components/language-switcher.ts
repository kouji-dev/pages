import { Component, ChangeDetectionStrategy, signal, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule, TranslatePipe } from '@ngx-translate/core';
import { Icon, Button } from 'shared-ui';
import { LanguageService, SupportedLanguage } from '../../application/services/language.service';

@Component({
  selector: 'app-language-switcher',
  imports: [CommonModule, TranslateModule, TranslatePipe, Icon, Button],
  template: `
    <div class="language-switcher">
      <button
        type="button"
        class="language-switcher_button"
        (click)="toggleDropdown()"
        [attr.aria-label]="'language.switchLanguage' | translate"
        [attr.aria-expanded]="isDropdownOpen()"
      >
        <lib-icon name="globe" size="md" class="language-switcher_icon" />
        <span class="language-switcher_current">{{ currentLanguageName() }}</span>
        <lib-icon
          name="chevron-down"
          size="sm"
          class="language-switcher_chevron"
          [class.language-switcher_chevron--open]="isDropdownOpen()"
        />
      </button>

      @if (isDropdownOpen()) {
        <div class="language-switcher_dropdown">
          @for (lang of supportedLanguages(); track lang.code) {
            <button
              type="button"
              class="language-switcher_item"
              [class.language-switcher_item--active]="lang.code === currentLanguage()"
              (click)="selectLanguage(lang.code)"
            >
              <span class="language-switcher_item-name">{{ lang.name }}</span>
              @if (lang.code === currentLanguage()) {
                <lib-icon name="check" size="sm" class="language-switcher_item-check" />
              }
            </button>
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .language-switcher {
        @apply relative;
      }

      .language-switcher_button {
        @apply flex items-center;
        @apply gap-2;
        @apply px-3 py-2;
        @apply rounded-md;
        @apply border border-border-default;
        @apply bg-bg-primary;
        @apply text-text-primary;
        @apply cursor-pointer;
        @apply transition-colors;
        @apply hover:bg-bg-hover;
        @apply active:bg-bg-active;
      }

      .language-switcher_icon {
        @apply flex-shrink-0;
      }

      .language-switcher_current {
        @apply text-sm;
        @apply font-medium;
        @apply min-w-[60px];
      }

      .language-switcher_chevron {
        @apply flex-shrink-0;
        @apply transition-transform;
      }

      .language-switcher_chevron--open {
        @apply rotate-180;
      }

      .language-switcher_dropdown {
        @apply absolute;
        @apply top-full;
        @apply right-0;
        @apply mt-2;
        @apply min-w-[160px];
        @apply bg-bg-primary;
        @apply border border-border-default;
        @apply rounded-lg;
        @apply shadow-lg;
        @apply z-50;
        @apply overflow-hidden;
      }

      .language-switcher_item {
        @apply flex items-center justify-between;
        @apply w-full;
        @apply px-4 py-3;
        @apply text-left;
        @apply bg-transparent;
        @apply border-none;
        @apply text-text-primary;
        @apply cursor-pointer;
        @apply transition-colors;
        @apply hover:bg-bg-hover;
      }

      .language-switcher_item--active {
        @apply bg-bg-secondary;
      }

      .language-switcher_item-name {
        @apply text-sm;
        @apply font-medium;
      }

      .language-switcher_item-check {
        @apply flex-shrink-0;
        @apply text-primary-500;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LanguageSwitcher {
  private readonly languageService = inject(LanguageService);

  readonly isDropdownOpen = signal<boolean>(false);
  readonly currentLanguage = this.languageService.currentLanguage;
  readonly supportedLanguages = computed(() => this.languageService.getSupportedLanguages());

  readonly currentLanguageName = computed(() => {
    const lang = this.currentLanguage();
    return this.languageService.getLanguageName(lang);
  });

  toggleDropdown(): void {
    this.isDropdownOpen.update((open) => !open);
  }

  selectLanguage(lang: SupportedLanguage): void {
    this.languageService.setLanguage(lang);
    this.isDropdownOpen.set(false);
  }
}
