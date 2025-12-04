import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Icon, IconName } from './icon';
import { Component } from '@angular/core';

// Host component to test the icon component
@Component({
  template: `
    <lib-icon
      [name]="iconName"
      [size]="size"
      [color]="color"
      [strokeWidth]="strokeWidth"
      [animation]="animation"
      [ariaLabel]="ariaLabel"
      [ariaHidden]="ariaHidden"
    ></lib-icon>
  `,
  standalone: true,
  imports: [Icon],
})
class TestHostComponent {
  iconName: IconName = 'menu';
  size: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' = 'md';
  color: string | undefined;
  strokeWidth = 2;
  animation: 'none' | 'spin' | 'pulse' | 'bounce' = 'none';
  ariaLabel = '';
  ariaHidden = false;
}

describe('Icon', () => {
  let hostComponent: TestHostComponent;
  let fixture: ComponentFixture<TestHostComponent>;
  let wrapperElement: HTMLElement | null;
  let lucideIconElement: HTMLElement | null;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Icon, TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    hostComponent = fixture.componentInstance;
    fixture.detectChanges();
    // Classes are now on the wrapper span element
    wrapperElement = fixture.nativeElement.querySelector('lib-icon span');
    lucideIconElement = fixture.nativeElement.querySelector('lucide-icon');
  });

  it('should create', () => {
    expect(hostComponent).toBeTruthy();
    expect(wrapperElement).toBeTruthy();
    expect(lucideIconElement).toBeTruthy();
  });

  it('should apply base icon class', () => {
    expect(wrapperElement?.classList.contains('icon')).toBe(true);
  });

  it('should render icon with default size and apply all classes', () => {
    expect(wrapperElement?.classList.contains('icon')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--md')).toBe(true);
    // Should not have animation class when animation is 'none'
    expect(wrapperElement?.classList.contains('icon--spin')).toBe(false);
    expect(wrapperElement?.classList.contains('icon--pulse')).toBe(false);
    expect(wrapperElement?.classList.contains('icon--bounce')).toBe(false);
  });

  it('should render icon with xs size and apply classes correctly', () => {
    hostComponent.size = 'xs';
    fixture.detectChanges();
    expect(wrapperElement?.classList.contains('icon')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--xs')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--md')).toBe(false);
  });

  it('should render icon with sm size and apply classes correctly', () => {
    hostComponent.size = 'sm';
    fixture.detectChanges();
    expect(wrapperElement?.classList.contains('icon')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--sm')).toBe(true);
  });

  it('should render icon with lg size and apply classes correctly', () => {
    hostComponent.size = 'lg';
    fixture.detectChanges();
    expect(wrapperElement?.classList.contains('icon')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--lg')).toBe(true);
  });

  it('should render icon with xl size and apply classes correctly', () => {
    hostComponent.size = 'xl';
    fixture.detectChanges();
    expect(wrapperElement?.classList.contains('icon')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--xl')).toBe(true);
  });

  it('should render icon with 2xl size and apply classes correctly', () => {
    hostComponent.size = '2xl';
    fixture.detectChanges();
    expect(wrapperElement?.classList.contains('icon')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--2xl')).toBe(true);
  });

  it('should apply spin animation class when loading (animation="spin")', () => {
    hostComponent.animation = 'spin';
    fixture.detectChanges();

    // Verify all classes are applied correctly
    expect(wrapperElement?.classList.contains('icon')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--md')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--spin')).toBe(true);

    // Should not have other animation classes
    expect(wrapperElement?.classList.contains('icon--pulse')).toBe(false);
    expect(wrapperElement?.classList.contains('icon--bounce')).toBe(false);
  });

  it('should apply pulse animation class correctly', () => {
    hostComponent.animation = 'pulse';
    fixture.detectChanges();

    expect(wrapperElement?.classList.contains('icon')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--md')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--pulse')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--spin')).toBe(false);
  });

  it('should apply bounce animation class correctly', () => {
    hostComponent.animation = 'bounce';
    fixture.detectChanges();

    expect(wrapperElement?.classList.contains('icon')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--md')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--bounce')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--spin')).toBe(false);
  });

  it('should apply size and animation classes together correctly', () => {
    hostComponent.size = 'lg';
    hostComponent.animation = 'spin';
    fixture.detectChanges();

    // All classes should be present
    expect(wrapperElement?.classList.contains('icon')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--lg')).toBe(true);
    expect(wrapperElement?.classList.contains('icon--spin')).toBe(true);

    // Verify class string format
    const classList = wrapperElement?.className.split(' ').filter(Boolean);
    expect(classList).toContain('icon');
    expect(classList).toContain('icon--lg');
    expect(classList).toContain('icon--spin');
    expect(classList?.length).toBe(3);
  });

  it('should not have empty strings in class list when animation is none', () => {
    hostComponent.animation = 'none';
    fixture.detectChanges();

    const classList = wrapperElement?.className.split(' ').filter(Boolean);
    // Should only have base icon class and size class
    expect(classList?.length).toBe(2);
    expect(classList).toContain('icon');
    expect(classList).toContain('icon--md');
    // No animation class should be present
    expect(classList).not.toContain('icon--spin');
    expect(classList).not.toContain('icon--pulse');
    expect(classList).not.toContain('icon--bounce');
  });

  it('should set aria-label on lucide-icon element when provided', () => {
    hostComponent.ariaLabel = 'Menu icon';
    fixture.detectChanges();
    expect(lucideIconElement?.getAttribute('aria-label')).toBe('Menu icon');
  });

  it('should set aria-hidden on lucide-icon element when true', () => {
    hostComponent.ariaHidden = true;
    fixture.detectChanges();
    expect(lucideIconElement?.getAttribute('aria-hidden')).toBe('true');
  });

  it('should convert kebab-case icon name to PascalCase', () => {
    hostComponent.iconName = 'chevron-down';
    fixture.detectChanges();
    // The src computed should convert 'chevron-down' to 'ChevronDown'
    expect(lucideIconElement).toBeTruthy();
  });

  it('should support different icon names', () => {
    const iconNames: IconName[] = ['menu', 'user', 'search', 'settings', 'home'];
    iconNames.forEach((name) => {
      hostComponent.iconName = name;
      fixture.detectChanges();
      expect(lucideIconElement).toBeTruthy();
    });
  });

  it('should have icons object accessible', () => {
    const iconComponent = fixture.debugElement.query((el) => el.name === 'lib-icon')
      ?.componentInstance as Icon;
    expect(iconComponent?.icons).toBeDefined();
  });
});
