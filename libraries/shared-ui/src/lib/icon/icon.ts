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

// Icon color names - maps to CSS variables
export type IconColor =
  // Semantic colors
  | 'primary'
  | 'secondary'
  | 'success'
  | 'warning'
  | 'error'
  | 'info'
  // Primary shades
  | 'primary-50'
  | 'primary-100'
  | 'primary-200'
  | 'primary-300'
  | 'primary-400'
  | 'primary-500'
  | 'primary-600'
  | 'primary-700'
  | 'primary-800'
  | 'primary-900'
  // Secondary shades
  | 'secondary-50'
  | 'secondary-100'
  | 'secondary-200'
  | 'secondary-300'
  | 'secondary-400'
  | 'secondary-500'
  | 'secondary-600'
  | 'secondary-700'
  | 'secondary-800'
  | 'secondary-900'
  // Text colors
  | 'text-primary'
  | 'text-secondary'
  | 'text-tertiary'
  | 'text-muted'
  | 'text-disabled'
  | 'text-inverse'
  | 'text-link'
  // Gray shades
  | 'gray-50'
  | 'gray-100'
  | 'gray-200'
  | 'gray-300'
  | 'gray-400'
  | 'gray-500'
  | 'gray-600'
  | 'gray-700'
  | 'gray-800'
  | 'gray-900';

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
    @if (src()) {
      <span [class]="iconClasses()">
        <lucide-icon
          [img]="src()!"
          [size]="computedSize()"
          [color]="computedColor()"
          [strokeWidth]="strokeWidth()"
          [attr.aria-label]="ariaLabel()"
          [attr.aria-hidden]="ariaHidden()"
        />
      </span>
    }
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
  color = input<IconColor | string>();
  strokeWidth = input<number>(2);
  animation = input<'none' | 'spin' | 'pulse' | 'bounce'>('none');
  ariaLabel = input<string>('');
  ariaHidden = input<boolean, boolean | string>(false, {
    transform: booleanAttribute,
  });

  /**
   * Map color name to CSS variable
   */
  private readonly colorMap: Record<IconColor, string> = {
    // Semantic colors
    primary: 'var(--color-primary)',
    secondary: 'var(--color-secondary)',
    success: 'var(--color-success)',
    warning: 'var(--color-warning)',
    error: 'var(--color-error)',
    info: 'var(--color-info)',
    // Primary shades
    'primary-50': 'var(--color-primary-50)',
    'primary-100': 'var(--color-primary-100)',
    'primary-200': 'var(--color-primary-200)',
    'primary-300': 'var(--color-primary-300)',
    'primary-400': 'var(--color-primary-400)',
    'primary-500': 'var(--color-primary-500)',
    'primary-600': 'var(--color-primary-600)',
    'primary-700': 'var(--color-primary-700)',
    'primary-800': 'var(--color-primary-800)',
    'primary-900': 'var(--color-primary-900)',
    // Secondary shades
    'secondary-50': 'var(--color-secondary-50)',
    'secondary-100': 'var(--color-secondary-100)',
    'secondary-200': 'var(--color-secondary-200)',
    'secondary-300': 'var(--color-secondary-300)',
    'secondary-400': 'var(--color-secondary-400)',
    'secondary-500': 'var(--color-secondary-500)',
    'secondary-600': 'var(--color-secondary-600)',
    'secondary-700': 'var(--color-secondary-700)',
    'secondary-800': 'var(--color-secondary-800)',
    'secondary-900': 'var(--color-secondary-900)',
    // Text colors
    'text-primary': 'var(--color-text-primary)',
    'text-secondary': 'var(--color-text-secondary)',
    'text-tertiary': 'var(--color-text-tertiary)',
    'text-muted': 'var(--color-text-muted)',
    'text-disabled': 'var(--color-text-disabled)',
    'text-inverse': 'var(--color-text-inverse)',
    'text-link': 'var(--color-text-link)',
    // Gray shades
    'gray-50': 'var(--color-gray-50)',
    'gray-100': 'var(--color-gray-100)',
    'gray-200': 'var(--color-gray-200)',
    'gray-300': 'var(--color-gray-300)',
    'gray-400': 'var(--color-gray-400)',
    'gray-500': 'var(--color-gray-500)',
    'gray-600': 'var(--color-gray-600)',
    'gray-700': 'var(--color-gray-700)',
    'gray-800': 'var(--color-gray-800)',
    'gray-900': 'var(--color-gray-900)',
  };

  /**
   * Get the CSS variable for the given color name, or return the string as-is if not in the map
   */
  readonly computedColor = computed<string | undefined>(() => {
    const colorName = this.color();
    if (!colorName) {
      return undefined;
    }
    // If it's a known color name, return the CSS variable
    if (colorName in this.colorMap) {
      return this.colorMap[colorName as IconColor];
    }
    // Otherwise, return the string as-is (for custom colors, hex codes, etc.)
    return colorName;
  });

  // Computed
  src = computed(() => {
    const iconName = this.name();
    if (!iconName || !iconName.trim()) {
      return null;
    }
    // Convert kebab-case to PascalCase for Lucide Angular icons
    const pascalCaseName = iconName
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join('');

    const icon = (icons as any)[pascalCaseName];
    return icon || null;
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
