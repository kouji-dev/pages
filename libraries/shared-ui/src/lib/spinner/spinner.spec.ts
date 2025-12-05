import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { Spinner, SpinnerSize, SpinnerColor } from './spinner';

// Host component to test the spinner component
@Component({
  template: `
    <lib-spinner [size]="size" [color]="color" [ariaLabel]="ariaLabel" [ariaHidden]="ariaHidden" />
  `,
  imports: [Spinner],
})
class TestHostComponent {
  size: SpinnerSize = 'md';
  color: SpinnerColor = 'default';
  ariaLabel = '';
  ariaHidden = false;
}

describe('Spinner', () => {
  let hostComponent: TestHostComponent;
  let fixture: ComponentFixture<TestHostComponent>;
  let spinnerComponent: Spinner;
  let spinnerElement: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Spinner, TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    hostComponent = fixture.componentInstance;
    spinnerComponent = fixture.debugElement.query((el) => el.name === 'lib-spinner')
      ?.componentInstance as Spinner;
    fixture.detectChanges();
    spinnerElement = fixture.nativeElement.querySelector('lib-spinner');
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

    expect(spinnerElement.classList.contains('spinner--sm')).toBe(true);
    expect(spinnerElement.classList.contains('spinner--md')).toBe(false);
  });

  it('should apply md size class', () => {
    hostComponent.size = 'md';
    fixture.detectChanges();

    expect(spinnerElement.classList.contains('spinner--md')).toBe(true);
  });

  it('should apply lg size class', () => {
    hostComponent.size = 'lg';
    fixture.detectChanges();

    expect(spinnerElement.classList.contains('spinner--lg')).toBe(true);
    expect(spinnerElement.classList.contains('spinner--md')).toBe(false);
  });

  it('should apply default color class', () => {
    hostComponent.color = 'default';
    fixture.detectChanges();

    expect(spinnerElement.classList.contains('spinner--default')).toBe(true);
  });

  it('should apply primary color class', () => {
    hostComponent.color = 'primary';
    fixture.detectChanges();

    expect(spinnerElement.classList.contains('spinner--primary')).toBe(true);
  });

  it('should apply secondary color class', () => {
    hostComponent.color = 'secondary';
    fixture.detectChanges();

    expect(spinnerElement.classList.contains('spinner--secondary')).toBe(true);
  });

  it('should apply white color class', () => {
    hostComponent.color = 'white';
    fixture.detectChanges();

    expect(spinnerElement.classList.contains('spinner--white')).toBe(true);
  });

  it('should set aria-label when provided', () => {
    hostComponent.ariaLabel = 'Loading content';
    fixture.detectChanges();

    expect(spinnerElement.getAttribute('aria-label')).toBe('Loading content');
  });

  it('should set default aria-label when not provided', () => {
    expect(spinnerElement.getAttribute('aria-label')).toBe('Loading');
  });

  it('should set aria-hidden when true', () => {
    hostComponent.ariaHidden = true;
    fixture.detectChanges();

    expect(spinnerElement.getAttribute('aria-hidden')).toBe('true');
  });

  it('should not set aria-hidden when false', () => {
    hostComponent.ariaHidden = false;
    fixture.detectChanges();

    expect(spinnerElement.getAttribute('aria-hidden')).toBeNull();
  });

  it('should have role="status"', () => {
    expect(spinnerElement.getAttribute('role')).toBe('status');
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

  it('should have spinner circle element', () => {
    const circleElement = fixture.nativeElement.querySelector('.spinner_circle');
    expect(circleElement).toBeTruthy();
  });

  it('should have spinner circle path element', () => {
    const pathElement = fixture.nativeElement.querySelector('.spinner_circle-path');
    expect(pathElement).toBeTruthy();
  });
});
