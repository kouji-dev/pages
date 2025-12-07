import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal, computed } from '@angular/core';
import { of, throwError } from 'rxjs';
import { ProfilePage } from './profile-page';
import { UserProfileService, UserProfile } from '../../application/services/user-profile.service';
import { ToastService } from 'shared-ui';
import { Button, Input, LoadingState, ErrorState } from 'shared-ui';

describe('ProfilePage', () => {
  let component: ProfilePage;
  let fixture: ComponentFixture<ProfilePage>;
  let userProfileService: UserProfileService;
  let toastService: ToastService;
  let element: HTMLElement;

  const mockProfile: UserProfile = {
    id: '1',
    name: 'Test User',
    email: 'test@example.com',
    avatarUrl: 'https://example.com/avatar.jpg',
    isActive: true,
    isVerified: true,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  };

  beforeEach(async () => {
    const mockUserProfileService = {
      userProfile: signal<UserProfile | undefined>(mockProfile),
      isLoading: computed(() => false),
      error: computed(() => undefined),
      hasError: computed(() => false),
      loadProfile: () => {},
      updateProfile: () => of(mockProfile),
    };

    const mockToastService = {
      success: () => {},
      error: () => {},
    };

    await TestBed.configureTestingModule({
      imports: [ProfilePage, Button, Input, LoadingState, ErrorState],
      providers: [
        { provide: UserProfileService, useValue: mockUserProfileService },
        { provide: ToastService, useValue: mockToastService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ProfilePage);
    component = fixture.componentInstance;
    userProfileService = TestBed.inject(UserProfileService);
    toastService = TestBed.inject(ToastService);
    element = fixture.nativeElement;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display page title and subtitle', () => {
    fixture.detectChanges();
    const title = element.querySelector('.profile-page_title');
    const subtitle = element.querySelector('.profile-page_subtitle');
    expect(title?.textContent?.trim()).toBe('Profile');
    expect(subtitle?.textContent?.trim()).toContain('Manage your account settings');
  });

  it('should display loading state when loading', () => {
    Object.defineProperty(userProfileService, 'isLoading', {
      get: () => computed(() => true),
      configurable: true,
    });
    fixture.detectChanges();
    const loadingState = element.querySelector('lib-loading-state');
    expect(loadingState).toBeTruthy();
  });

  it('should display error state when there is an error', () => {
    Object.defineProperty(userProfileService, 'hasError', {
      get: () => computed(() => true),
      configurable: true,
    });
    Object.defineProperty(userProfileService, 'error', {
      get: () => computed(() => new Error('Test error')),
      configurable: true,
    });
    fixture.detectChanges();
    const errorState = element.querySelector('lib-error-state');
    expect(errorState).toBeTruthy();
  });

  it('should display error state when profile is not found', () => {
    Object.defineProperty(userProfileService, 'userProfile', {
      get: () => signal<UserProfile | undefined>(undefined),
      configurable: true,
    });
    Object.defineProperty(userProfileService, 'isLoading', {
      get: () => computed(() => false),
      configurable: true,
    });
    Object.defineProperty(userProfileService, 'hasError', {
      get: () => computed(() => false),
      configurable: true,
    });
    fixture.detectChanges();
    const errorState = element.querySelector('lib-error-state');
    expect(errorState).toBeTruthy();
  });

  it('should display profile form when profile is loaded', () => {
    fixture.detectChanges();
    const form = element.querySelector('.profile-page_form');
    expect(form).toBeTruthy();
  });

  it('should initialize form fields with profile data', () => {
    fixture.detectChanges();
    expect(component.name()).toBe('Test User');
    expect(component.email()).toBe('test@example.com');
  });

  it('should display name input with current value', () => {
    fixture.detectChanges();
    const nameInput = element.querySelector('lib-input[label="Name"]');
    expect(nameInput).toBeTruthy();
  });

  it('should display email input as readonly', () => {
    fixture.detectChanges();
    const emailInput = element.querySelector('lib-input[label="Email"]');
    expect(emailInput).toBeTruthy();
  });

  it('should validate name field - required', () => {
    fixture.detectChanges();
    component.name.set('');
    fixture.detectChanges();
    expect(component.nameError()).toBe('Name is required');
    expect(component.isFormValid()).toBe(false);
  });

  it('should validate name field - minimum length', () => {
    fixture.detectChanges();
    component.name.set('A');
    fixture.detectChanges();
    expect(component.nameError()).toBe('Name must be at least 2 characters');
    expect(component.isFormValid()).toBe(false);
  });

  it('should validate name field - valid', () => {
    fixture.detectChanges();
    component.name.set('Valid Name');
    fixture.detectChanges();
    expect(component.nameError()).toBe('');
    expect(component.isFormValid()).toBe(true);
  });

  it('should detect changes when name is modified', () => {
    fixture.detectChanges();
    expect(component.hasChanges()).toBe(false);
    component.name.set('New Name');
    fixture.detectChanges();
    expect(component.hasChanges()).toBe(true);
  });

  it('should disable save button when form is invalid', () => {
    fixture.detectChanges();
    component.name.set('');
    fixture.detectChanges();
    const saveButton = element.querySelector('lib-button[type="submit"]');
    expect(saveButton?.getAttribute('ng-reflect-disabled')).toBe('true');
  });

  it('should disable save button when there are no changes', () => {
    fixture.detectChanges();
    const saveButton = element.querySelector('lib-button[type="submit"]');
    expect(saveButton?.getAttribute('ng-reflect-disabled')).toBe('true');
  });

  it('should enable save button when form is valid and has changes', () => {
    fixture.detectChanges();
    component.name.set('New Name');
    fixture.detectChanges();
    const saveButton = element.querySelector('lib-button[type="submit"]');
    expect(saveButton?.getAttribute('ng-reflect-disabled')).toBe('false');
  });

  it('should call updateProfile when form is submitted', async () => {
    let updateProfileCalled = false;
    let updateProfileArgs: any = null;
    (userProfileService as any).updateProfile = (args: any) => {
      updateProfileCalled = true;
      updateProfileArgs = args;
      return of(mockProfile);
    };
    fixture.detectChanges();
    component.name.set('Updated Name');
    fixture.detectChanges();

    await component.handleSaveProfile();

    expect(updateProfileCalled).toBe(true);
    expect(updateProfileArgs).toEqual({ name: 'Updated Name' });
  });

  it('should show success toast after successful update', async () => {
    let successCalled = false;
    let successMessage = '';
    (userProfileService as any).updateProfile = () => of(mockProfile);
    (toastService as any).success = (message: string) => {
      successCalled = true;
      successMessage = message;
    };
    fixture.detectChanges();
    component.name.set('Updated Name');
    fixture.detectChanges();

    await component.handleSaveProfile();

    expect(successCalled).toBe(true);
    expect(successMessage).toBe('Profile updated successfully!');
  });

  it('should show error toast when update fails', async () => {
    const error = new Error('Update failed');
    let errorCalled = false;
    let errorMessage = '';
    (userProfileService as any).updateProfile = () => throwError(() => error);
    (toastService as any).error = (message: string) => {
      errorCalled = true;
      errorMessage = message;
    };
    fixture.detectChanges();
    component.name.set('Updated Name');
    fixture.detectChanges();

    await component.handleSaveProfile();

    expect(errorCalled).toBe(true);
    expect(errorMessage).toBe('Update failed');
  });

  it('should reset form when cancel is clicked', () => {
    fixture.detectChanges();
    component.name.set('Changed Name');
    fixture.detectChanges();
    expect(component.name()).toBe('Changed Name');

    component.handleReset();
    fixture.detectChanges();

    expect(component.name()).toBe('Test User');
    expect(component.hasChanges()).toBe(false);
  });

  it('should call loadProfile when retry is clicked', () => {
    let loadProfileCalled = false;
    (userProfileService as any).loadProfile = () => {
      loadProfileCalled = true;
    };
    component.handleRetry();
    expect(loadProfileCalled).toBe(true);
  });

  it('should display change password form section', () => {
    fixture.detectChanges();
    const changePasswordForm = element.querySelector('app-change-password-form');
    expect(changePasswordForm).toBeTruthy();
  });

  it('should display avatar upload section', () => {
    fixture.detectChanges();
    const avatarUpload = element.querySelector('app-avatar-upload');
    expect(avatarUpload).toBeTruthy();
  });

  it('should not save when form is invalid', async () => {
    let updateProfileCalled = false;
    (userProfileService as any).updateProfile = () => {
      updateProfileCalled = true;
      return of(mockProfile);
    };
    fixture.detectChanges();
    component.name.set('');
    fixture.detectChanges();

    await component.handleSaveProfile();

    expect(updateProfileCalled).toBe(false);
  });

  it('should not save when there are no changes', async () => {
    let updateProfileCalled = false;
    (userProfileService as any).updateProfile = () => {
      updateProfileCalled = true;
      return of(mockProfile);
    };
    fixture.detectChanges();

    await component.handleSaveProfile();

    expect(updateProfileCalled).toBe(false);
  });
});
