import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component, signal } from '@angular/core';
import { Input, InputType } from './input';

// Host component to test the input component
@Component({
  template: `
    <lib-input
      [type]="type"
      [placeholder]="placeholder"
      [label]="label"
      [helperText]="helperText"
      [errorMessage]="errorMessage"
      [required]="required"
      [disabled]="disabled"
      [readonly]="readonly"
      [leftIcon]="leftIcon"
      [rightIcon]="rightIcon"
      [showPasswordToggle]="showPasswordToggle"
      [(model)]="value"
      (focused)="onFocused($event)"
      (blurred)="onBlurred($event)"
    />
  `,
  imports: [Input],
})
class TestHostComponent {
  type: InputType = 'text';
  placeholder = '';
  label = '';
  helperText = '';
  errorMessage = '';
  required = false;
  disabled = false;
  readonly = false;
  leftIcon: string | null = null;
  rightIcon: string | null = null;
  showPasswordToggle = false;
  value = signal('');
  focusedEvent: FocusEvent | null = null;
  blurredEvent: FocusEvent | null = null;

  onFocused(event: FocusEvent): void {
    this.focusedEvent = event;
  }

  onBlurred(event: FocusEvent): void {
    this.blurredEvent = event;
  }
}

describe('Input', () => {
  let hostComponent: TestHostComponent;
  let fixture: ComponentFixture<TestHostComponent>;
  let inputComponent: Input;
  let inputElement: HTMLInputElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Input, TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    hostComponent = fixture.componentInstance;
    inputComponent = fixture.debugElement.query((el) => el.name === 'lib-input')
      ?.componentInstance as Input;
    fixture.detectChanges();
    inputElement = fixture.nativeElement.querySelector('input');
  });

  it('should create', () => {
    expect(inputComponent).toBeTruthy();
    expect(inputElement).toBeTruthy();
  });

  it('should have default type of text', () => {
    expect(inputComponent.type()).toBe('text');
  });

  it('should apply error class when errorMessage is set', () => {
    hostComponent.errorMessage = 'This is an error';
    fixture.detectChanges();

    expect(inputElement.classList.contains('input--error')).toBe(true);
  });

  it('should apply disabled class when disabled is true', () => {
    hostComponent.disabled = true;
    fixture.detectChanges();

    expect(inputElement.disabled).toBe(true);
    expect(inputElement.classList.contains('input--disabled')).toBe(true);
  });

  it('should apply readonly class when readonly is true', () => {
    hostComponent.readonly = true;
    fixture.detectChanges();

    expect(inputElement.readOnly).toBe(true);
    expect(inputElement.classList.contains('input--readonly')).toBe(true);
  });

  it('should display label when provided', () => {
    hostComponent.label = 'Test Label';
    fixture.detectChanges();

    const labelElement = fixture.nativeElement.querySelector('.input-label');
    expect(labelElement).toBeTruthy();
    expect(labelElement.textContent.trim()).toBe('Test Label');
  });

  it('should display required asterisk when required is true', () => {
    hostComponent.label = 'Test Label';
    hostComponent.required = true;
    fixture.detectChanges();

    const requiredElement = fixture.nativeElement.querySelector('.input-label-required');
    expect(requiredElement).toBeTruthy();
    expect(requiredElement.textContent.trim()).toBe('*');
  });

  it('should display helper text when provided and no error', () => {
    hostComponent.helperText = 'Helper text';
    fixture.detectChanges();

    const helperTextElement = fixture.nativeElement.querySelector('.input-helper-text');
    expect(helperTextElement).toBeTruthy();
    expect(helperTextElement.textContent.trim()).toBe('Helper text');
  });

  it('should display error message when provided', () => {
    hostComponent.errorMessage = 'Error message';
    fixture.detectChanges();

    const errorElement = fixture.nativeElement.querySelector('.input-error-message');
    expect(errorElement).toBeTruthy();
    expect(errorElement.textContent.trim()).toContain('Error message');
  });

  it('should not display helper text when error message is present', () => {
    hostComponent.helperText = 'Helper text';
    hostComponent.errorMessage = 'Error message';
    fixture.detectChanges();

    const helperTextElement = fixture.nativeElement.querySelector('.input-helper-text');
    expect(helperTextElement).toBeFalsy();
  });

  it('should emit focused event on focus', () => {
    const focusEvent = new FocusEvent('focus');
    inputElement.dispatchEvent(focusEvent);
    fixture.detectChanges();

    expect(hostComponent.focusedEvent).toBeTruthy();
  });

  it('should emit blurred event on blur', () => {
    const blurEvent = new FocusEvent('blur');
    inputElement.dispatchEvent(blurEvent);
    fixture.detectChanges();

    expect(hostComponent.blurredEvent).toBeTruthy();
  });

  it('should update model value on input', () => {
    inputElement.value = 'test value';
    const event = new Event('input', { bubbles: true });
    inputElement.dispatchEvent(event);
    fixture.detectChanges();

    expect(hostComponent.value()).toBe('test value');
  });

  it('should display left icon when provided', () => {
    hostComponent.leftIcon = 'search';
    fixture.detectChanges();

    const iconElement = fixture.nativeElement.querySelector('.input-icon--left');
    expect(iconElement).toBeTruthy();
  });

  it('should display right icon when provided', () => {
    hostComponent.rightIcon = 'x';
    fixture.detectChanges();

    const iconElement = fixture.nativeElement.querySelector('.input-icon--right');
    expect(iconElement).toBeTruthy();
  });

  it('should show password toggle for password type when enabled', () => {
    hostComponent.type = 'password';
    hostComponent.showPasswordToggle = true;
    fixture.detectChanges();

    const toggleButton = fixture.nativeElement.querySelector('.input-password-toggle');
    expect(toggleButton).toBeTruthy();
  });

  it('should toggle password visibility on button click', () => {
    hostComponent.type = 'password';
    hostComponent.showPasswordToggle = true;
    fixture.detectChanges();

    const toggleButton = fixture.nativeElement.querySelector(
      '.input-password-toggle',
    ) as HTMLButtonElement;
    const inputEl = fixture.nativeElement.querySelector('input') as HTMLInputElement;

    expect(inputEl.type).toBe('password');

    toggleButton.click();
    fixture.detectChanges();

    expect(inputEl.type).toBe('text');
  });
});

describe('Input with two-way binding', () => {
  @Component({
    template: `<lib-input [(model)]="value" />`,
    imports: [Input],
  })
  class TestComponent {
    value = signal('initial');
  }

  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Input, TestComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should bind value two-way', () => {
    const inputComponent = fixture.debugElement.query((el) => el.name === 'lib-input')
      ?.componentInstance as Input;

    expect(inputComponent.model()).toBe('initial');

    const inputElement = fixture.nativeElement.querySelector('input') as HTMLInputElement;
    inputElement.value = 'updated';
    const event = new Event('input', { bubbles: true });
    inputElement.dispatchEvent(event);
    fixture.detectChanges();

    expect(component.value()).toBe('updated');
  });
});
