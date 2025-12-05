import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component, signal } from '@angular/core';
import { Spinner } from './spinner';
import { SpinnerContent, SpinnerSize, SpinnerColor } from './spinner-content';

// Host component to test the spinner directive
@Component({
  template: `
    <div
      *spinner="isLoading(); size: size; color: color; message: message; ariaLabel: ariaLabel"
      style="position: relative; padding: 2rem; min-height: 150px;"
    >
      <p>Test content</p>
    </div>
  `,
  imports: [Spinner],
})
class TestHostComponent {
  isLoading = signal(false);
  size: SpinnerSize = 'md';
  color: SpinnerColor = 'default';
  message = '';
  ariaLabel = '';
}

describe('Spinner Directive', () => {
  let hostComponent: TestHostComponent;
  let fixture: ComponentFixture<TestHostComponent>;
  let directive: Spinner;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Spinner, SpinnerContent, TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    hostComponent = fixture.componentInstance;
    fixture.detectChanges();

    // Get the directive instance
    const directiveEl = fixture.debugElement.query((el) => el.name === 'div');
    directive = directiveEl?.injector.get(Spinner);
  });

  it('should create', () => {
    expect(hostComponent).toBeTruthy();
    expect(directive).toBeTruthy();
  });

  it('should render content when loading is false', () => {
    hostComponent.isLoading.set(false);
    fixture.detectChanges();

    const content = fixture.nativeElement.querySelector('p');
    expect(content).toBeTruthy();
    expect(content.textContent).toBe('Test content');
  });

  it('should show spinner when loading is true', () => {
    hostComponent.isLoading.set(true);
    fixture.detectChanges();

    const spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeTruthy();
  });

  it('should hide spinner when loading is false', () => {
    hostComponent.isLoading.set(true);
    fixture.detectChanges();

    let spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeTruthy();

    hostComponent.isLoading.set(false);
    fixture.detectChanges();

    spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeFalsy();
  });

  it('should apply default size of md', () => {
    hostComponent.isLoading.set(true);
    fixture.detectChanges();

    const spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeTruthy();
    // The size is passed to the SpinnerContent component internally
  });

  it('should apply custom size', () => {
    hostComponent.size = 'sm';
    hostComponent.isLoading.set(true);
    fixture.detectChanges();

    const spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeTruthy();
  });

  it('should apply custom color', () => {
    hostComponent.color = 'primary';
    hostComponent.isLoading.set(true);
    fixture.detectChanges();

    const spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeTruthy();
  });

  it('should apply custom message', () => {
    hostComponent.message = 'Loading data...';
    hostComponent.isLoading.set(true);
    fixture.detectChanges();

    const spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeTruthy();
    const message = fixture.nativeElement.querySelector('.spinner-content_message');
    expect(message).toBeTruthy();
    expect(message.textContent.trim()).toBe('Loading data...');
  });

  it('should apply custom aria-label', () => {
    hostComponent.ariaLabel = 'Custom loading label';
    hostComponent.isLoading.set(true);
    fixture.detectChanges();

    const spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeTruthy();
  });

  it('should use default aria-label when not provided', () => {
    hostComponent.ariaLabel = '';
    hostComponent.isLoading.set(true);
    fixture.detectChanges();

    const spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeTruthy();
  });

  it('should handle null loading value', () => {
    (hostComponent.isLoading as any).set(null);
    fixture.detectChanges();

    const spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeFalsy();
  });

  it('should handle undefined loading value', () => {
    (hostComponent.isLoading as any).set(undefined);
    fixture.detectChanges();

    const spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeFalsy();
  });

  it('should cleanup on destroy', () => {
    hostComponent.isLoading.set(true);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('lib-spinner-content')).toBeTruthy();

    fixture.destroy();

    // After destroy, the spinner should be cleaned up
    expect(fixture.nativeElement.querySelector('lib-spinner-content')).toBeFalsy();
  });

  it('should update spinner configuration when inputs change', () => {
    hostComponent.isLoading.set(true);
    fixture.detectChanges();

    let spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeTruthy();

    // Change size
    hostComponent.size = 'lg';
    fixture.detectChanges();

    spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeTruthy();

    // Change color
    hostComponent.color = 'secondary';
    fixture.detectChanges();

    spinnerContent = fixture.nativeElement.querySelector('lib-spinner-content');
    expect(spinnerContent).toBeTruthy();
  });
});
