import { Component, input, ChangeDetectionStrategy, computed, inject } from '@angular/core';
import { Icon } from 'shared-ui';
import { getIssueTypeConfig, type IssueType } from '../../helpers/issue-helpers';
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-issue-type-badge',
  standalone: true,
  imports: [Icon],
  template: `
    <span class="issue-type-badge" [class]="badgeClasses()">
      <lib-icon [name]="typeConfig().icon" [size]="'xs'" />
      <span>{{ typeLabel() }}</span>
    </span>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .issue-type-badge {
        @apply inline-flex items-center gap-1.5;
        @apply px-2 py-1;
        @apply text-xs font-semibold;
        @apply rounded;
        @apply uppercase;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IssueTypeBadge {
  private readonly translateService = inject(TranslateService);

  readonly type = input.required<IssueType>();

  readonly customLabel = input<string | undefined>(undefined);

  readonly typeConfig = computed(() => getIssueTypeConfig(this.type()));

  readonly badgeClasses = computed(() => {
    const config = this.typeConfig();
    return `${config.bgColor} ${config.textColor}`;
  });

  readonly typeLabel = computed(() => {
    const customLabel = this.customLabel();
    if (customLabel) return customLabel;
    const typeKey = this.type();
    return this.translateService.instant(`issues.type.${typeKey}`);
  });
}
