import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { SpinnerContent, SpinnerSize, SpinnerColor } from './spinner-content';

// Host component to test the spinner content component
@Component({
  template: `
    <lib-spinner-content
      [size]="size"
      [color]="color"
      [message]="message"
      [ariaLabel]="ariaLabel"
    />
  `,
  imports: [SpinnerContent],
})
class TestHostComponent {
  size: SpinnerSize = 'md';
  color: SpinnerColor = 'default';
  message = '';
  ariaLabel = '';
}

describe('SpinnerContent', () => {
  let hostComponent: TestHostComponent;
  let fixture: ComponentFixture<TestHostComponent>;
  let spinnerComponent: SpinnerContent;
  let spinnerElement: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SpinnerContent, TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    hostComponent = fixture.componentInstance;
    spinnerComponent = fixture.debugElement.query((el) => el.name === 'lib-spinner-content')
      ?.componentInstance as SpinnerContent;
    fixture.detectChanges();
    spinnerElement = fixture.nativeElement.querySelector('lib-spinner-content');
  });

  it('should create', () => {
    expect(spinnerComponent).toBeTruthy();
    expect(spinnerElement).toBeTruthy();
  });

  it('should have default size of md', () => {
    expect(spinnerComponent.size()).toBe('md');
  });

  it('should have default color of default', () => {
    expect(spinnerComponent.color()).toBe('default');
  });

  it('should apply sm size class', () => {
    hostComponent.size = 'sm';
    fixture.detectChanges();

    const spinner = spinnerElement.querySelector('.spinner');
    expect(spinner?.classList.contains('spinner--sm')).toBe(true);
    expect(spinner?.classList.contains('spinner--md')).toBe(false);
  });

  it('should apply md size class', () => {
    hostComponent.size = 'md';
    fixture.detectChanges();

    const spinner = spinnerElement.querySelector('.spinner');
    expect(spinner?.classList.contains('spinner--md')).toBe(true);
  });

  it('should apply lg size class', () => {
    hostComponent.size = 'lg';
    fixture.detectChanges();

    const spinner = spinnerElement.querySelector('.spinner');
    expect(spinner?.classList.contains('spinner--lg')).toBe(true);
    expect(spinner?.classList.contains('spinner--md')).toBe(false);
  });

  it('should apply default color class', () => {
    hostComponent.color = 'default';
    fixture.detectChanges();

    const spinner = spinnerElement.querySelector('.spinner');
    expect(spinner?.classList.contains('spinner--default')).toBe(true);
  });

  it('should apply primary color class', () => {
    hostComponent.color = 'primary';
    fixture.detectChanges();

    const spinner = spinnerElement.querySelector('.spinner');
    expect(spinner?.classList.contains('spinner--primary')).toBe(true);
  });

  it('should apply secondary color class', () => {
    hostComponent.color = 'secondary';
    fixture.detectChanges();

    const spinner = spinnerElement.querySelector('.spinner');
    expect(spinner?.classList.contains('spinner--secondary')).toBe(true);
  });

  it('should apply white color class', () => {
    hostComponent.color = 'white';
    fixture.detectChanges();

    const spinner = spinnerElement.querySelector('.spinner');
    expect(spinner?.classList.contains('spinner--white')).toBe(true);
  });

  it('should set aria-label when provided', () => {
    hostComponent.ariaLabel = 'Loading content';
    fixture.detectChanges();

    const spinner = spinnerElement.querySelector('.spinner');
    expect(spinner?.getAttribute('aria-label')).toBe('Loading content');
  });

  it('should set default aria-label when not provided', () => {
    hostComponent.ariaLabel = '';
    fixture.detectChanges();

    const spinner = spinnerElement.querySelector('.spinner');
    expect(spinner?.getAttribute('aria-label')).toBe('Loading');
  });

  it('should have role="status"', () => {
    const spinner = spinnerElement.querySelector('.spinner');
    expect(spinner?.getAttribute('role')).toBe('status');
  });

  it('should compute correct size for sm', () => {
    hostComponent.size = 'sm';
    fixture.detectChanges();

    expect(spinnerComponent.computedSize()).toBe(16);
  });

  it('should compute correct size for md', () => {
    hostComponent.size = 'md';
    fixture.detectChanges();

    expect(spinnerComponent.computedSize()).toBe(20);
  });

  it('should compute correct size for lg', () => {
    hostComponent.size = 'lg';
    fixture.detectChanges();

    expect(spinnerComponent.computedSize()).toBe(24);
  });

  it('should display message when provided', () => {
    hostComponent.message = 'Loading data...';
    fixture.detectChanges();

    const message = spinnerElement.querySelector('.spinner-content_message');
    expect(message).toBeTruthy();
    expect(message?.textContent?.trim()).toBe('Loading data...');
  });

  it('should not display message when not provided', () => {
    hostComponent.message = '';
    fixture.detectChanges();

    const message = spinnerElement.querySelector('.spinner-content_message');
    expect(message).toBeFalsy();
  });

  it('should have spinner-content container', () => {
    const container = spinnerElement.querySelector('.spinner-content');
    expect(container).toBeTruthy();
  });

  it('should have backdrop', () => {
    const backdrop = spinnerElement.querySelector('.spinner-content_backdrop');
    expect(backdrop).toBeTruthy();
  });

  it('should have loader container', () => {
    const loader = spinnerElement.querySelector('.spinner-content_loader');
    expect(loader).toBeTruthy();
  });

  it('should have spinner circle element', () => {
    const circleElement = spinnerElement.querySelector('.spinner_circle');
    expect(circleElement).toBeTruthy();
  });

  it('should have spinner circle path element', () => {
    const pathElement = spinnerElement.querySelector('.spinner_circle-path');
    expect(pathElement).toBeTruthy();
  });
});
