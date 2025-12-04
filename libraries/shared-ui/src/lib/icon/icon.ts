import {
  ChangeDetectionStrategy,
  Component,
  input,
  computed,
  booleanAttribute,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { LucideAngularModule, icons } from 'lucide-angular';

export type IconSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';

// Convert PascalCase icon names to kebab-case for better developer experience
type PascalCaseToKebabCase<S extends string> = S extends `${infer P1}${infer P2}`
  ? P2 extends Uncapitalize<P2>
    ? `${Uncapitalize<P1>}${PascalCaseToKebabCase<P2>}`
    : `${Uncapitalize<P1>}-${PascalCaseToKebabCase<Uncapitalize<P2>>}`
  : S;

// Extract icon names and convert to kebab-case
export type IconName = PascalCaseToKebabCase<keyof typeof icons>;

@Component({
  selector: 'lib-icon',
  imports: [CommonModule, LucideAngularModule],
  template: `
    <span [class]="iconClasses()">
      <lucide-icon
        [img]="src()"
        [size]="computedSize()"
        [color]="color() || undefined"
        [strokeWidth]="strokeWidth()"
        [attr.aria-label]="ariaLabel()"
        [attr.aria-hidden]="ariaHidden()"
      />
    </span>
  `,
  styles: [
    `
      @reference "#theme";

      .icon {
        @apply inline-flex items-center justify-center;
        flex-shrink: 0;
        /* Inherit color from parent so icons work in buttons with different text colors */
        color: inherit;
      }

      /* Ensure the lucide-icon inside inherits the color */
      .icon lucide-icon {
        color: inherit;
      }

      /* Size variants */
      .icon--xs {
        @apply w-3 h-3;
      }

      .icon--sm {
        @apply w-4 h-4;
      }

      .icon--md {
        @apply w-5 h-5;
      }

      .icon--lg {
        @apply w-6 h-6;
      }

      .icon--xl {
        @apply w-8 h-8;
      }

      .icon--2xl {
        @apply w-12 h-12;
      }

      /* Animation variants - Using Tailwind CSS 4 built-in animations */
      .icon--spin {
        @apply animate-spin;
      }

      .icon--pulse {
        @apply animate-pulse;
      }

      .icon--bounce {
        @apply animate-bounce;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Icon {
  // Icons object for standalone usage
  readonly icons = icons;

  // Inputs
  name = input.required<IconName>();
  size = input<IconSize>('md');
  color = input<string>();
  strokeWidth = input<number>(2);
  animation = input<'none' | 'spin' | 'pulse' | 'bounce'>('none');
  ariaLabel = input<string>('');
  ariaHidden = input<boolean, boolean | string>(false, {
    transform: booleanAttribute,
  });

  // Computed
  src = computed(() => {
    const iconName = this.name();
    // Convert kebab-case to PascalCase for Lucide Angular icons
    const pascalCaseName = iconName
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join('');

    return (icons as any)[pascalCaseName];
  });

  iconClasses = computed(() => {
    const size = this.size();
    const animation = this.animation();

    const classes = ['icon', `icon--${size}`];
    if (animation !== 'none') {
      classes.push(`icon--${animation}`);
    }
    return classes.join(' ');
  });

  computedSize = computed(() => {
    const size = this.size();
    const sizeMap: Record<IconSize, number> = {
      xs: 12,
      sm: 16,
      md: 20,
      lg: 24,
      xl: 32,
      '2xl': 48,
    };

    return sizeMap[size] || 20;
  });
}
