import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { UserMenu } from './user-menu';
import { AuthService } from '../../application/services/auth.service';
import { Component } from '@angular/core';
import { Icon } from 'shared-ui';

@Component({
  template: ` <app-user-menu /> `,
  standalone: true,
  imports: [UserMenu],
})
class TestHostComponent {}

describe('UserMenu', () => {
  let component: UserMenu;
  let fixture: ComponentFixture<TestHostComponent>;
  let authService: AuthService;
  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserMenu, Icon, TestHostComponent],
      providers: [
        AuthService,
        {
          provide: Router,
          useValue: {
            navigate: jasmine.createSpy('navigate'),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    authService = TestBed.inject(AuthService);
    router = TestBed.inject(Router);
    const userMenuElement = fixture.nativeElement.querySelector('app-user-menu');
    component = fixture.debugElement.children[0].componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display user name', () => {
    const userName = fixture.nativeElement.querySelector('.user-menu_name');
    expect(userName).toBeTruthy();
    expect(userName.textContent).toContain('John Doe');
  });

  it('should toggle menu when trigger is clicked', () => {
    expect(component.isOpen()).toBe(false);

    const trigger = fixture.nativeElement.querySelector('.user-menu_trigger');
    trigger.click();
    fixture.detectChanges();

    expect(component.isOpen()).toBe(true);

    const dropdown = fixture.nativeElement.querySelector('.user-menu_dropdown');
    expect(dropdown).toBeTruthy();
  });

  it('should display user info in dropdown', () => {
    component.isOpen.set(true);
    fixture.detectChanges();

    const userInfoName = fixture.nativeElement.querySelector('.user-menu_user-info-name');
    const userInfoEmail = fixture.nativeElement.querySelector('.user-menu_user-info-email');

    expect(userInfoName).toBeTruthy();
    expect(userInfoName.textContent).toContain('John Doe');
    expect(userInfoEmail).toBeTruthy();
    expect(userInfoEmail.textContent).toContain('john@example.com');
  });

  it('should display profile and settings links', () => {
    component.isOpen.set(true);
    fixture.detectChanges();

    const links = fixture.nativeElement.querySelectorAll('.user-menu_item');
    expect(links.length).toBeGreaterThan(0);

    const profileLink = fixture.nativeElement.querySelector('a[routerLink="/profile"]');
    const settingsLink = fixture.nativeElement.querySelector('a[routerLink="/settings"]');

    expect(profileLink).toBeTruthy();
    expect(settingsLink).toBeTruthy();
  });

  it('should call logout when logout button is clicked', () => {
    spyOn(authService, 'logout');

    component.isOpen.set(true);
    fixture.detectChanges();

    const logoutButton = fixture.nativeElement.querySelector('.user-menu_item--logout');
    logoutButton.click();
    fixture.detectChanges();

    expect(authService.logout).toHaveBeenCalled();
    expect(component.isOpen()).toBe(false);
  });

  it('should close menu when clicking outside', () => {
    component.isOpen.set(true);
    fixture.detectChanges();

    const clickEvent = new MouseEvent('click', { bubbles: true });
    document.dispatchEvent(clickEvent);
    fixture.detectChanges();

    expect(component.isOpen()).toBe(false);
  });

  it('should display initials when no avatar', () => {
    const placeholder = fixture.nativeElement.querySelector('.user-menu_avatar-placeholder');
    expect(placeholder).toBeTruthy();
    expect(placeholder.textContent).toContain('JD');
  });
});
