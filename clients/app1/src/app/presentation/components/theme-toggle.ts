import { Component, ChangeDetectionStrategy, inject, computed } from '@angular/core';
import { Button } from 'shared-ui';
import { ThemeService } from '../../application/services/theme.service';
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-theme-toggle',
  imports: [Button],
  template: `
    <lib-button
      variant="ghost"
      size="md"
      [iconOnly]="true"
      [leftIcon]="iconName()"
      (clicked)="themeService.toggleTheme()"
      [attr.aria-label]="ariaLabel()"
      [attr.title]="ariaLabel()"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class ThemeToggle {
  readonly themeService = inject(ThemeService);
  private readonly translateService = inject(TranslateService);

  readonly iconName = computed<'sun' | 'moon'>(() => {
    return this.themeService.theme() === 'dark' ? 'sun' : 'moon';
  });

  readonly ariaLabel = computed<string>(() => {
    return this.themeService.theme() === 'dark'
      ? this.translateService.instant('common.switchToLightMode')
      : this.translateService.instant('common.switchToDarkMode');
  });
}
