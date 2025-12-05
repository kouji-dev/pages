import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LoadingState } from './loading-state';
import { Component } from '@angular/core';

@Component({
  template: `
    <lib-loading-state [message]="message" [size]="size" [color]="color" [ariaLabel]="ariaLabel" />
  `,
  standalone: true,
  imports: [LoadingState],
})
class TestHostComponent {
  message = '';
  size: 'sm' | 'md' | 'lg' = 'md';
  color: 'default' | 'primary' | 'secondary' = 'default';
  ariaLabel = '';
}

describe('LoadingState', () => {
  let hostComponent: TestHostComponent;
  let fixture: ComponentFixture<TestHostComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoadingState, TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    hostComponent = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(hostComponent).toBeTruthy();
    expect(fixture.nativeElement.querySelector('lib-loading-state')).toBeTruthy();
  });

  it('should display spinner icon', () => {
    const icon = fixture.nativeElement.querySelector('lib-icon');
    expect(icon).toBeTruthy();
    expect(icon.getAttribute('ng-reflect-name')).toBe('loader');
  });

  it('should display message when provided', () => {
    hostComponent.message = 'Loading data...';
    fixture.detectChanges();

    const message = fixture.nativeElement.querySelector('.loading-state_message');
    expect(message).toBeTruthy();
    expect(message.textContent.trim()).toBe('Loading data...');
  });

  it('should not display message when empty', () => {
    hostComponent.message = '';
    fixture.detectChanges();

    const message = fixture.nativeElement.querySelector('.loading-state_message');
    expect(message).toBeFalsy();
  });

  it('should apply default aria-label when not provided', () => {
    const icon = fixture.nativeElement.querySelector('lib-icon');
    expect(icon.getAttribute('ng-reflect-aria-label')).toBe('Loading');
  });

  it('should apply custom aria-label when provided', () => {
    hostComponent.ariaLabel = 'Custom loading label';
    fixture.detectChanges();

    const icon = fixture.nativeElement.querySelector('lib-icon');
    expect(icon.getAttribute('ng-reflect-aria-label')).toBe('Custom loading label');
  });
});
