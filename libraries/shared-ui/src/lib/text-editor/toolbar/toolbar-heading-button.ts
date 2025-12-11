import { Component, ChangeDetectionStrategy, input, inject, computed } from '@angular/core';
import { Button } from '../../button/button';
import { IconName } from '../../icon/icon';
import { HeadingPlugin } from '../plugins/heading-plugin';
import { HeadingTagType } from '@lexical/rich-text';

@Component({
  selector: 'lib-toolbar-heading-button',
  imports: [Button],
  template: `
    <lib-button
      variant="ghost"
      size="sm"
      [leftIcon]="iconName()"
      (clicked)="insertHeading()"
      [attr.title]="'Heading ' + tag()"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolbarHeadingButton {
  private readonly plugin = inject(HeadingPlugin);
  readonly tag = input.required<HeadingTagType>();

  readonly iconName = computed<IconName | null>(() => {
    const tag = this.tag();
    if (tag === 'h1') return 'heading1';
    if (tag === 'h2') return 'heading2';
    if (tag === 'h3') return 'heading3';
    return null;
  });

  insertHeading(): void {
    this.plugin.insertHeading(this.tag());
  }
}
