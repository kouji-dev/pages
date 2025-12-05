import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ErrorState } from './error-state';
import { Component } from '@angular/core';

@Component({
  template: `
    <lib-error-state
      [title]="title"
      [message]="message"
      [retryLabel]="retryLabel"
      [showRetry]="showRetry"
      (onRetry)="onRetry()"
    />
  `,
  standalone: true,
  imports: [ErrorState],
})
class TestHostComponent {
  title = '';
  message = '';
  retryLabel = 'Try Again';
  showRetry = true;
  retryClicked = false;

  onRetry(): void {
    this.retryClicked = true;
  }
}

describe('ErrorState', () => {
  let hostComponent: TestHostComponent;
  let fixture: ComponentFixture<TestHostComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ErrorState, TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    hostComponent = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(hostComponent).toBeTruthy();
    expect(fixture.nativeElement.querySelector('lib-error-state')).toBeTruthy();
  });

  it('should display error icon', () => {
    const icon = fixture.nativeElement.querySelector('lib-icon');
    expect(icon).toBeTruthy();
    expect(icon.getAttribute('ng-reflect-name')).toBe('circle-alert');
  });

  it('should display default title when not provided', () => {
    const title = fixture.nativeElement.querySelector('.error-state_title');
    expect(title).toBeTruthy();
    expect(title.textContent.trim()).toBe('Something went wrong');
  });

  it('should display custom title when provided', () => {
    hostComponent.title = 'Connection Error';
    fixture.detectChanges();

    const title = fixture.nativeElement.querySelector('.error-state_title');
    expect(title.textContent.trim()).toBe('Connection Error');
  });

  it('should display message when provided', () => {
    hostComponent.message = 'Unable to connect to server';
    fixture.detectChanges();

    const message = fixture.nativeElement.querySelector('.error-state_message');
    expect(message).toBeTruthy();
    expect(message.textContent.trim()).toBe('Unable to connect to server');
  });

  it('should not display message when empty', () => {
    hostComponent.message = '';
    fixture.detectChanges();

    const message = fixture.nativeElement.querySelector('.error-state_message');
    expect(message).toBeFalsy();
  });

  it('should display retry button when showRetry is true', () => {
    hostComponent.showRetry = true;
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('lib-button');
    expect(button).toBeTruthy();
  });

  it('should not display retry button when showRetry is false', () => {
    hostComponent.showRetry = false;
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('lib-button');
    expect(button).toBeFalsy();
  });

  it('should display default retry label', () => {
    hostComponent.showRetry = true;
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('lib-button');
    expect(button.textContent.trim()).toBe('Try Again');
  });

  it('should display custom retry label', () => {
    hostComponent.showRetry = true;
    hostComponent.retryLabel = 'Retry Connection';
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('lib-button');
    expect(button.textContent.trim()).toBe('Retry Connection');
  });

  it('should emit onRetry when retry button is clicked', () => {
    hostComponent.showRetry = true;
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('lib-button');
    button.click();
    fixture.detectChanges();

    expect(hostComponent.retryClicked).toBe(true);
  });
});
