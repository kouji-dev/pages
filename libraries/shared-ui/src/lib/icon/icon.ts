import {
  ChangeDetectionStrategy,
  Component,
  input,
  computed,
  booleanAttribute,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { LucideAngularModule, icons } from 'lucide-angular';
import { IconName, lucideIconNames } from './icon-names';

export type IconSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';

// Icon color names - maps to CSS variables
export type IconColor =
  // Semantic colors (New System)
  | 'foreground'
  | 'muted-foreground'
  | 'card-foreground'
  | 'popover-foreground'
  | 'primary-foreground'
  | 'secondary-foreground'
  | 'accent-foreground'
  | 'destructive-foreground'
  | 'error-foreground'
  | 'success-foreground'
  | 'warning-foreground'
  | 'navigation-foreground'
  | 'navigation-accent-foreground'
  
  // Base colors
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'destructive'
  | 'error'
  | 'success'
  | 'warning'
  | 'border'
  | 'input'
  | 'ring'

  // Legacy colors (Deprecated - to be migrated)
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
  // 'text-tertiary' removed - use muted-foreground
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

// Re-export IconName and lucideIconNames from icon-names.ts
export type { IconName } from './icon-names';
export { lucideIconNames } from './icon-names';

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
    // Semantic colors (New System)
    'foreground': 'var(--color-foreground)',
    'muted-foreground': 'var(--color-muted-foreground)',
    'card-foreground': 'var(--color-card-foreground)',
    'popover-foreground': 'var(--color-popover-foreground)',
    'primary-foreground': 'var(--color-primary-foreground)',
    'secondary-foreground': 'var(--color-secondary-foreground)',
    'accent-foreground': 'var(--color-accent-foreground)',
    'destructive-foreground': 'var(--color-error-foreground)',
    'error-foreground': 'var(--color-error-foreground)',
    'success-foreground': 'var(--color-success-foreground)',
    'warning-foreground': 'var(--color-warning-foreground)',
    'navigation-foreground': 'var(--color-navigation-foreground)',
    'navigation-accent-foreground': 'var(--color-navigation-accent-foreground)',
    
    'primary': 'var(--color-primary)',
    'secondary': 'var(--color-secondary)',
    'accent': 'var(--color-accent)',
    'destructive': 'var(--color-error)',
    'error': 'var(--color-error)',
    'success': 'var(--color-success)',
    'warning': 'var(--color-warning)',
    'border': 'var(--color-border)',
    'input': 'var(--color-input)',
    'ring': 'var(--color-ring)',

    // Legacy colors - error is now the primary semantic name
    info: 'var(--color-primary)',
    
    // Primary shades
    'primary-50': 'var(--color-primary)',
    'primary-100': 'var(--color-primary)',
    'primary-200': 'var(--color-primary)',
    'primary-300': 'var(--color-primary)',
    'primary-400': 'var(--color-primary)',
    'primary-500': 'var(--color-primary)',
    'primary-600': 'var(--color-primary)',
    'primary-700': 'var(--color-primary)',
    'primary-800': 'var(--color-primary)',
    'primary-900': 'var(--color-primary)',
    
    // Secondary shades - using muted/secondary tokens
    'secondary-50': 'var(--color-secondary)',
    'secondary-100': 'var(--color-secondary)',
    'secondary-200': 'var(--color-secondary)',
    'secondary-300': 'var(--color-secondary)',
    'secondary-400': 'var(--color-secondary)',
    'secondary-500': 'var(--color-secondary)',
    'secondary-600': 'var(--color-secondary)',
    'secondary-700': 'var(--color-secondary)',
    'secondary-800': 'var(--color-secondary)',
    'secondary-900': 'var(--color-secondary)',
    
    // Text colors
    'text-primary': 'var(--color-foreground)',
    'text-secondary': 'var(--color-muted-foreground)',
    // 'text-tertiary' removed - use muted-foreground
    'text-muted': 'var(--color-muted-foreground)',
    'text-disabled': 'var(--color-muted-foreground)',
    'text-inverse': 'var(--color-background)',
    'text-link': 'var(--color-primary)',
    
    // Gray shades
    'gray-50': 'var(--color-muted)',
    'gray-100': 'var(--color-muted)',
    'gray-200': 'var(--color-muted)',
    'gray-300': 'var(--color-muted)',
    'gray-400': 'var(--color-muted)',
    'gray-500': 'var(--color-muted-foreground)',
    'gray-600': 'var(--color-muted-foreground)',
    'gray-700': 'var(--color-muted-foreground)',
    'gray-800': 'var(--color-foreground)',
    'gray-900': 'var(--color-foreground)',
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
