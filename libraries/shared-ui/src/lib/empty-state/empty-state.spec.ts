import { ComponentFixture, TestBed } from '@angular/core/testing';
import { EmptyState } from './empty-state';
import { Component } from '@angular/core';

@Component({
  template: `
    <lib-empty-state
      [title]="title"
      [message]="message"
      [icon]="icon"
      [iconLabel]="iconLabel"
      [actionLabel]="actionLabel"
      [actionIcon]="actionIcon"
      [actionVariant]="actionVariant"
      (onAction)="onAction()"
    />
  `,
  standalone: true,
  imports: [EmptyState],
})
class TestHostComponent {
  title = '';
  message = '';
  icon: string | undefined = undefined;
  iconLabel = '';
  actionLabel = '';
  actionIcon: string | undefined = undefined;
  actionVariant: 'primary' | 'secondary' | 'danger' | 'ghost' = 'primary';
  actionClicked = false;

  onAction(): void {
    this.actionClicked = true;
  }
}

describe('EmptyState', () => {
  let hostComponent: TestHostComponent;
  let fixture: ComponentFixture<TestHostComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EmptyState, TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    hostComponent = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(hostComponent).toBeTruthy();
    expect(fixture.nativeElement.querySelector('lib-empty-state')).toBeTruthy();
  });

  it('should display default title when not provided', () => {
    const title = fixture.nativeElement.querySelector('.empty-state_title');
    expect(title).toBeTruthy();
    expect(title.textContent.trim()).toBe('No items found');
  });

  it('should display custom title when provided', () => {
    hostComponent.title = 'No projects';
    fixture.detectChanges();

    const title = fixture.nativeElement.querySelector('.empty-state_title');
    expect(title.textContent.trim()).toBe('No projects');
  });

  it('should display message when provided', () => {
    hostComponent.message = 'Get started by creating your first project';
    fixture.detectChanges();

    const message = fixture.nativeElement.querySelector('.empty-state_message');
    expect(message).toBeTruthy();
    expect(message.textContent.trim()).toBe('Get started by creating your first project');
  });

  it('should not display message when empty', () => {
    hostComponent.message = '';
    fixture.detectChanges();

    const message = fixture.nativeElement.querySelector('.empty-state_message');
    expect(message).toBeFalsy();
  });

  it('should display icon when provided', () => {
    hostComponent.icon = 'folder';
    fixture.detectChanges();

    const icon = fixture.nativeElement.querySelector('lib-icon');
    expect(icon).toBeTruthy();
    expect(icon.getAttribute('ng-reflect-name')).toBe('folder');
  });

  it('should not display icon when not provided', () => {
    hostComponent.icon = undefined;
    fixture.detectChanges();

    const icons = fixture.nativeElement.querySelectorAll('lib-icon');
    expect(icons.length).toBe(0);
  });

  it('should display action button when actionLabel is provided', () => {
    hostComponent.actionLabel = 'Create Project';
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('lib-button');
    expect(button).toBeTruthy();
    expect(button.textContent.trim()).toBe('Create Project');
  });

  it('should not display action button when actionLabel is empty', () => {
    hostComponent.actionLabel = '';
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('lib-button');
    expect(button).toBeFalsy();
  });

  it('should display action icon when provided', () => {
    hostComponent.actionLabel = 'Add Item';
    hostComponent.actionIcon = 'plus';
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('lib-button');
    expect(button).toBeTruthy();
    // The icon should be rendered inside the button
    const icon = button.querySelector('lib-icon');
    expect(icon).toBeTruthy();
  });

  it('should emit onAction when action button is clicked', () => {
    hostComponent.actionLabel = 'Create';
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('lib-button');
    button.click();
    fixture.detectChanges();

    expect(hostComponent.actionClicked).toBe(true);
  });
});
