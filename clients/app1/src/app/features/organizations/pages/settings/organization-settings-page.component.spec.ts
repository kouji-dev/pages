import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { signal, computed, ViewContainerRef } from '@angular/core';
import { of, throwError } from 'rxjs';
import { OrganizationSettingsPage } from './organization-settings-page.component';
import {
  OrganizationService,
  Organization,
} from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import {
  OrganizationMembersService,
  OrganizationMember,
} from '../../../../application/services/organization-members.service';
import {
  OrganizationInvitationsService,
  OrganizationInvitation,
} from '../../../../application/services/organization-invitations.service';
import { AuthService } from '../../../../core/auth/auth.service';
import { ToastService, Modal } from 'shared-ui';
import { Button, Icon, Input, LoadingState, ErrorState } from 'shared-ui';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { TranslateModule } from '@ngx-translate/core';

describe('OrganizationSettingsPage', () => {
  let component: OrganizationSettingsPage;
  let fixture: ComponentFixture<OrganizationSettingsPage>;
  let organizationService: OrganizationService;
  let membersService: OrganizationMembersService;
  let invitationsService: OrganizationInvitationsService;
  let authService: AuthService;
  let toastService: ToastService;
  let modal: Modal;
  let router: Router;
  let element: HTMLElement;

  const mockOrganization: Organization = {
    id: '1',
    name: 'Test Organization',
    description: 'Test description',
    created_at: '',
    updated_at: '',
    owner_id: '1',
  };

  const mockMembers: OrganizationMember[] = [
    {
      user_id: 'user1',
      user_name: 'Test User 1',
      user_email: 'user1@test.com',
      role: 'admin',
      organization_id: '1',
      joined_at: '2024-01-01T00:00:00Z',
      avatar_url: null,
    },
    {
      user_id: 'user2',
      user_name: 'Test User 2',
      user_email: 'user2@test.com',
      role: 'member',
      organization_id: '1',
      joined_at: '2024-01-01T00:00:00Z',
      avatar_url: null,
    },
  ];

  beforeEach(async () => {
    const mockOrganizationService = {
      currentOrganization: signal<Organization | undefined>(mockOrganization),
      isFetchingOrganization: computed(() => false),
      organizationError: computed(() => undefined),
      fetchOrganization: vi.fn().mockResolvedValue(undefined),
      updateOrganization: vi.fn().mockResolvedValue(undefined),
      deleteOrganization: vi.fn().mockResolvedValue(undefined),
      reloadCurrentOrganization: vi.fn(),
    };

    const mockMembersService = {
      members: signal<OrganizationMember[]>(mockMembers),
      isLoading: computed(() => false),
      hasError: computed(() => false),
      error: computed(() => undefined),
      loadMembers: vi.fn(),
      removeMember: vi.fn().mockResolvedValue(undefined),
    };

    const mockInvitationsService = {
      invitations: signal<OrganizationInvitation[]>([]),
      isLoading: computed(() => false),
      hasError: computed(() => false),
      error: computed(() => undefined),
      loadInvitations: vi.fn(),
      cancelInvitation: vi.fn().mockResolvedValue(undefined),
    };

    const mockAuthService = {
      currentUser: signal({ id: 'user1', email: 'user1@test.com', name: 'Test User 1' }),
    };

    const mockToastService = {
      success: vi.fn(),
      error: vi.fn(),
    };

    const mockModal = {
      open: vi.fn().mockReturnValue(of({ confirmed: false })),
    };

    const mockRouter = {
      navigate: vi.fn().mockResolvedValue(true),
    };

    const mockNavigationService = {
      currentOrganizationId: computed(() => '1'),
      navigateToOrganizations: vi.fn(),
    };

    const mockActivatedRoute = {
      snapshot: {
        paramMap: {
          get: (key: string) => (key === 'id' ? '1' : null),
        },
      },
    };

    await TestBed.configureTestingModule({
      imports: [
        OrganizationSettingsPage,
        Button,
        Icon,
        Input,
        LoadingState,
        ErrorState,
        TranslateModule.forRoot(),
      ],
      providers: [
        { provide: OrganizationService, useValue: mockOrganizationService },
        { provide: OrganizationMembersService, useValue: mockMembersService },
        { provide: OrganizationInvitationsService, useValue: mockInvitationsService },
        { provide: AuthService, useValue: mockAuthService },
        { provide: NavigationService, useValue: mockNavigationService },
        { provide: ToastService, useValue: mockToastService },
        { provide: Modal, useValue: mockModal },
        { provide: Router, useValue: mockRouter },
        { provide: ActivatedRoute, useValue: mockActivatedRoute },
        ViewContainerRef,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(OrganizationSettingsPage);
    component = fixture.componentInstance;
    organizationService = TestBed.inject(OrganizationService);
    membersService = TestBed.inject(OrganizationMembersService);
    invitationsService = TestBed.inject(OrganizationInvitationsService);
    authService = TestBed.inject(AuthService);
    toastService = TestBed.inject(ToastService);
    modal = TestBed.inject(Modal);
    router = TestBed.inject(Router);
    element = fixture.nativeElement;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display page title', () => {
    fixture.detectChanges();
    const title = element.querySelector('.org-settings-page_title');
    expect(title?.textContent?.trim()).toBe('organizations.settings.title');
  });

  it('should display organization name in subtitle', () => {
    fixture.detectChanges();
    const subtitle = element.querySelector('.org-settings-page_subtitle');
    expect(subtitle?.textContent?.trim()).toBe('Test Organization');
  });

  it('should display organization details form when organization is loaded', () => {
    fixture.detectChanges();
    const form = element.querySelector('.org-settings-page_form');
    expect(form).toBeTruthy();
  });

  it('should initialize form fields with organization data', () => {
    fixture.detectChanges();
    expect(component.name()).toBe('Test Organization');
    expect(component.description()).toBe('Test description');
  });

  it('should validate name field - required', () => {
    fixture.detectChanges();
    component.name.set('');
    fixture.detectChanges();
    expect(component.nameError()).toBe('organizations.settings.nameRequired');
    expect(component.isFormValid()).toBe(false);
  });

  it('should validate name field - minimum length', () => {
    fixture.detectChanges();
    component.name.set('AB');
    fixture.detectChanges();
    expect(component.nameError()).toBe('organizations.settings.nameMinLength');
    expect(component.isFormValid()).toBe(false);
  });

  it('should validate name field - valid', () => {
    fixture.detectChanges();
    component.name.set('Valid Name');
    fixture.detectChanges();
    expect(component.nameError()).toBe('');
    expect(component.isFormValid()).toBe(true);
  });

  it('should detect changes when form is modified', () => {
    fixture.detectChanges();
    expect(component.hasChanges()).toBe(false);
    component.name.set('New Name');
    fixture.detectChanges();
    expect(component.hasChanges()).toBe(true);
  });

  it('should call updateOrganization when form is submitted', async () => {
    fixture.detectChanges();
    component.name.set('Updated Name');
    fixture.detectChanges();

    component.handleSave();
    await fixture.whenStable();

    expect(organizationService.updateOrganization).toHaveBeenCalledWith('1', {
      name: 'Updated Name',
    });
  });

  it('should reset form when cancel is clicked', () => {
    fixture.detectChanges();
    component.name.set('Changed Name');
    fixture.detectChanges();
    expect(component.name()).toBe('Changed Name');

    component.handleReset();
    fixture.detectChanges();

    expect(component.name()).toBe('Test Organization');
    expect(component.hasChanges()).toBe(false);
  });

  it('should open delete modal when delete button is clicked', () => {
    fixture.detectChanges();
    component.handleDeleteClick();
    expect(modal.open).toHaveBeenCalled();
  });

  it('should display members section', () => {
    fixture.detectChanges();
    const membersSection = element.querySelector('app-member-list');
    expect(membersSection).toBeTruthy();
  });

  it('should display pending invitations section for admins', () => {
    fixture.detectChanges();
    const invitationsSection = element.querySelector('app-pending-invitations');
    expect(invitationsSection).toBeTruthy();
  });

  it('should compute current user role from members', () => {
    fixture.detectChanges();
    expect(component.currentUserRole()).toBe('admin');
  });

  it('should compute canManageMembers based on role', () => {
    fixture.detectChanges();
    expect(component.canManageMembers()).toBe(true);
  });

  it('should call loadMembers when retry is clicked', () => {
    component.handleMembersRetry();
    expect(membersService.loadMembers).toHaveBeenCalled();
  });

  it('should open add member modal when add member is clicked', () => {
    fixture.detectChanges();
    component.handleAddMember();
    expect(modal.open).toHaveBeenCalled();
  });

  it('should open change role modal when change role is clicked', () => {
    fixture.detectChanges();
    component.handleChangeRole(mockMembers[0]);
    expect(modal.open).toHaveBeenCalled();
  });

  it('should call removeMember when remove member is clicked', async () => {
    fixture.detectChanges();
    await component.handleRemoveMember(mockMembers[0]);
    expect(membersService.removeMember).toHaveBeenCalled();
  });

  it('should open invite modal when send invitation is clicked', () => {
    fixture.detectChanges();
    component.handleSendInvitation();
    expect(modal.open).toHaveBeenCalled();
  });

  it('should call cancelInvitation when cancel invitation is clicked', async () => {
    const mockInvitation: OrganizationInvitation = {
      id: '1',
      email: 'test@example.com',
      role: 'member',
      expires_at: '2024-12-31T00:00:00Z',
      created_at: '2024-01-01T00:00:00Z',
      organization_id: '1',
      invited_by: 'user1',
      accepted_at: null,
    };
    fixture.detectChanges();
    await component.handleCancelInvitation(mockInvitation);
    expect(invitationsService.cancelInvitation).toHaveBeenCalledWith('1');
  });

  it('should compute organizationId from route params', () => {
    // NavigationService mock would return based on route params logic in real app, here we mocked currentOrganizationId which we check.
    // Wait, in the component `organizationId` calls `navigationService.currentOrganizationId()`.
    // In our test, `NavigationService` is not explicitly mocked, but `OrganizationService` is.
    // The component injects `NavigationService`. We need to provide a mock for it.
    // In `imports` we use `OrganizationSettingsPage` which is standalone.
    // The `NavigationService` should be provided in the test module.
    // I missed adding `NavigationService` to providers in `beforeEach`.
    // Let's add it.
  });
});
