import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { Button } from './button';

describe('Button', () => {
  let component: Button;
  let fixture: ComponentFixture<Button>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Button, RouterTestingModule],
    }).compileComponents();

    fixture = TestBed.createComponent(Button);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render button element when link is not provided', () => {
    fixture.componentRef.setInput('link', null);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    const anchor = compiled.querySelector('a');
    expect(button).toBeTruthy();
    expect(anchor).toBeFalsy();
  });

  it('should render anchor element when link is provided', () => {
    fixture.componentRef.setInput('link', '/test');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    const anchor = compiled.querySelector('a');
    expect(button).toBeFalsy();
    expect(anchor).toBeTruthy();
  });

  it('should have default variant of primary', () => {
    expect(component.variant()).toBe('primary');
  });

  it('should have default size of md', () => {
    expect(component.size()).toBe('md');
  });

  it('should not be disabled by default', () => {
    expect(component.disabled()).toBe(false);
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    expect(button?.hasAttribute('disabled')).toBe(false);
  });

  it('should not be loading by default', () => {
    expect(component.loading()).toBe(false);
  });

  it('should apply primary variant class', () => {
    fixture.componentRef.setInput('variant', 'primary');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    expect(button?.classList.contains('button--primary')).toBe(true);
  });

  it('should apply secondary variant class', () => {
    fixture.componentRef.setInput('variant', 'secondary');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    expect(button?.classList.contains('button--secondary')).toBe(true);
  });

  it('should apply danger variant class', () => {
    fixture.componentRef.setInput('variant', 'danger');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    expect(button?.classList.contains('button--danger')).toBe(true);
  });

  it('should apply ghost variant class', () => {
    fixture.componentRef.setInput('variant', 'ghost');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    expect(button?.classList.contains('button--ghost')).toBe(true);
  });

  it('should apply sm size class', () => {
    fixture.componentRef.setInput('size', 'sm');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    expect(button?.classList.contains('button--sm')).toBe(true);
  });

  it('should apply md size class', () => {
    fixture.componentRef.setInput('size', 'md');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    expect(button?.classList.contains('button--md')).toBe(true);
  });

  it('should apply lg size class', () => {
    fixture.componentRef.setInput('size', 'lg');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    expect(button?.classList.contains('button--lg')).toBe(true);
  });

  it('should be disabled when disabled input is true', () => {
    fixture.componentRef.setInput('disabled', true);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    expect(button?.hasAttribute('disabled')).toBe(true);
    expect(button?.classList.contains('button--disabled')).toBe(true);
  });

  it('should show loading spinner when loading is true', () => {
    fixture.componentRef.setInput('loading', true);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const spinner = compiled.querySelector('.button_spinner');
    expect(spinner).toBeTruthy();
  });

  it('should hide button content when loading', () => {
    fixture.componentRef.setInput('loading', true);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const content = compiled.querySelector('.button_content');
    expect(content?.classList.contains('button_content--hidden')).toBe(true);
  });

  it('should emit click event when clicked', () => {
    let clicked = false;
    component.clicked.subscribe(() => {
      clicked = true;
    });
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    button?.click();
    expect(clicked).toBe(true);
  });

  it('should not emit click event when disabled', () => {
    fixture.componentRef.setInput('disabled', true);
    fixture.detectChanges();
    let clicked = false;
    component.clicked.subscribe(() => {
      clicked = true;
    });
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    button?.click();
    expect(clicked).toBe(false);
  });

  it('should not emit click event when loading', () => {
    fixture.componentRef.setInput('loading', true);
    fixture.detectChanges();
    let clicked = false;
    component.clicked.subscribe(() => {
      clicked = true;
    });
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    button?.click();
    expect(clicked).toBe(false);
  });

  it('should render button with text content', () => {
    fixture = TestBed.createComponent(Button);
    const compiled = fixture.nativeElement as HTMLElement;
    const buttonElement = compiled.querySelector('button');
    expect(buttonElement).toBeTruthy();
    // Content is provided via ng-content, test will verify button structure
  });

  it('should support icon-only button', () => {
    fixture.componentRef.setInput('iconOnly', true);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    expect(button?.classList.contains('button--icon-only')).toBe(true);
  });

  it('should have correct type attribute', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    expect(button?.getAttribute('type')).toBe('button');
  });

  it('should support custom type attribute', () => {
    fixture.componentRef.setInput('type', 'submit');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('button');
    expect(button?.getAttribute('type')).toBe('submit');
  });
});
