import { Component, ChangeDetectionStrategy, inject, computed } from '@angular/core';
import { Button } from 'shared-ui';
import { ThemeService } from '../../application/services/theme.service';

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

  readonly iconName = computed<'sun' | 'moon'>(() => {
    return this.themeService.theme() === 'dark' ? 'sun' : 'moon';
  });

  readonly ariaLabel = computed<string>(() => {
    return this.themeService.theme() === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
  });
}
