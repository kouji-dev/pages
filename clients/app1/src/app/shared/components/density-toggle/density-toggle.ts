import { Component, ChangeDetectionStrategy, inject, computed } from '@angular/core';
import { Button, IconName } from 'shared-ui';
import { DensityService } from '../../../core/services/density.service';
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-density-toggle',
  imports: [Button],
  template: `
    <lib-button
      variant="ghost"
      size="md"
      [iconOnly]="true"
      [leftIcon]="iconName()"
      (clicked)="densityService.toggleDensity()"
      [attr.aria-label]="ariaLabel()"
      [attr.title]="ariaLabel()"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class DensityToggle {
  readonly densityService = inject(DensityService);
  private readonly translateService = inject(TranslateService);

  readonly iconName = computed<IconName>(() => {
    return this.densityService.density() === 'compact' ? 'maximize-2' : 'minimize-2';
  });

  readonly ariaLabel = computed<string>(() => {
    return this.densityService.density() === 'compact'
      ? this.translateService.instant('common.switchToDefaultDensity') || 'Switch to default density'
      : this.translateService.instant('common.switchToCompactDensity') || 'Switch to compact density';
  });
}

