import { Component, ChangeDetectionStrategy, signal, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslatePipe } from '@ngx-translate/core';
import { Button } from 'shared-ui';
import { LanguageService, SupportedLanguage } from '../../application/services/language.service';

@Component({
  selector: 'app-language-switcher',
  imports: [CommonModule, TranslatePipe, Button],
  template: `
    <div class="language-switcher">
      <lib-button
        variant="ghost"
        size="md"
        leftIcon="globe"
        [rightIcon]="isDropdownOpen() ? 'chevron-up' : 'chevron-down'"
        (clicked)="toggleDropdown()"
        [attr.aria-label]="'language.switchLanguage' | translate"
        [attr.aria-expanded]="isDropdownOpen()"
        class="language-switcher_button"
      >
        {{ currentLanguageName() }}
      </lib-button>

      @if (isDropdownOpen()) {
        <div class="language-switcher_dropdown">
          @for (lang of supportedLanguages(); track lang.code) {
            <lib-button
              variant="ghost"
              size="md"
              [rightIcon]="lang.code === currentLanguage() ? 'check' : null"
              [class.language-switcher_item--active]="lang.code === currentLanguage()"
              (clicked)="selectLanguage(lang.code)"
              [fullWidth]="true"
              class="language-switcher_item"
            >
              {{ lang.name }}
            </lib-button>
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
        @apply min-w-[100px];
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
        @apply flex flex-col;
      }

      .language-switcher_item {
        @apply justify-start;
      }

      .language-switcher_item--active {
        @apply bg-bg-secondary;
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
