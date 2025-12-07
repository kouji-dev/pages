import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { signal, computed } from '@angular/core';
import { of, throwError } from 'rxjs';
import { OrganizationSettingsPage } from './organization-settings-page';
import { OrganizationService, Organization } from '../../application/services/organization.service';
import {
  OrganizationMembersService,
  OrganizationMember,
} from '../../application/services/organization-members.service';
import {
  OrganizationInvitationsService,
  OrganizationInvitation,
} from '../../application/services/organization-invitations.service';
import { AuthService } from '../../application/services/auth.service';
import { ToastService, Modal } from 'shared-ui';
import { Button, Icon, Input, LoadingState, ErrorState } from 'shared-ui';
import { ViewContainerRef } from '@angular/core';

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
    slug: 'test-org',
    description: 'Test description',
    memberCount: 5,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  };

  const mockMembers: OrganizationMember[] = [
    {
      user_id: 'user1',
      user_name: 'Test User 1',
      user_email: 'user1@test.com',
      role: 'admin',
    },
    {
      user_id: 'user2',
      user_name: 'Test User 2',
      user_email: 'user2@test.com',
      role: 'member',
    },
  ];

  beforeEach(async () => {
    const mockOrganizationService = {
      currentOrganization: signal<Organization | undefined>(mockOrganization),
      isFetchingOrganization: computed(() => false),
      organizationError: computed(() => undefined),
      fetchOrganization: () => Promise.resolve(),
      updateOrganization: () => Promise.resolve(),
      deleteOrganization: () => Promise.resolve(),
    };

    const mockMembersService = {
      members: signal<OrganizationMember[]>(mockMembers),
      isLoading: computed(() => false),
      hasError: computed(() => false),
      error: computed(() => undefined),
      loadMembers: () => {},
      removeMember: () => Promise.resolve(),
    };

    const mockInvitationsService = {
      invitations: signal<OrganizationInvitation[]>([]),
      isLoading: computed(() => false),
      hasError: computed(() => false),
      error: computed(() => undefined),
      loadInvitations: () => {},
      cancelInvitation: () => Promise.resolve(),
    };

    const mockAuthService = {
      currentUser: signal({ id: 'user1', email: 'user1@test.com', name: 'Test User 1' }),
    };

    const mockToastService = {
      success: () => {},
      error: () => {},
    };

    const mockModal = {
      open: () => of({ confirmed: false }),
    };

    const mockRouter = {
      navigate: () => Promise.resolve(true),
    };

    const mockActivatedRoute = {
      snapshot: {
        paramMap: {
          get: (key: string) => (key === 'id' ? '1' : null),
        },
      },
    };

    await TestBed.configureTestingModule({
      imports: [OrganizationSettingsPage, Button, Icon, Input, LoadingState, ErrorState],
      providers: [
        { provide: OrganizationService, useValue: mockOrganizationService },
        { provide: OrganizationMembersService, useValue: mockMembersService },
        { provide: OrganizationInvitationsService, useValue: mockInvitationsService },
        { provide: AuthService, useValue: mockAuthService },
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
    expect(title?.textContent?.trim()).toBe('Organization Settings');
  });

  it('should display organization name in subtitle', () => {
    fixture.detectChanges();
    const subtitle = element.querySelector('.org-settings-page_subtitle');
    expect(subtitle?.textContent?.trim()).toBe('Test Organization');
  });

  it('should display loading state when loading', () => {
    Object.defineProperty(organizationService, 'isFetchingOrganization', {
      get: () => computed(() => true),
      configurable: true,
    });
    fixture.detectChanges();
    const loadingState = element.querySelector('lib-loading-state');
    expect(loadingState).toBeTruthy();
  });

  it('should display error state when there is an error', () => {
    Object.defineProperty(organizationService, 'organizationError', {
      get: () => computed(() => new Error('Test error')),
      configurable: true,
    });
    fixture.detectChanges();
    const errorState = element.querySelector('lib-error-state');
    expect(errorState).toBeTruthy();
  });

  it('should display error state when organization is not found', () => {
    Object.defineProperty(organizationService, 'currentOrganization', {
      get: () => signal<Organization | undefined>(undefined),
      configurable: true,
    });
    Object.defineProperty(organizationService, 'isFetchingOrganization', {
      get: () => computed(() => false),
      configurable: true,
    });
    Object.defineProperty(organizationService, 'organizationError', {
      get: () => computed(() => undefined),
      configurable: true,
    });
    fixture.detectChanges();
    const errorState = element.querySelector('lib-error-state');
    expect(errorState).toBeTruthy();
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
    expect(component.nameError()).toBe('Organization name is required');
    expect(component.isFormValid()).toBe(false);
  });

  it('should validate name field - minimum length', () => {
    fixture.detectChanges();
    component.name.set('AB');
    fixture.detectChanges();
    expect(component.nameError()).toBe('Organization name must be at least 3 characters');
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
    let updateCalled = false;
    let updateArgs: any = null;
    (organizationService as any).updateOrganization = (id: string, data: any) => {
      updateCalled = true;
      updateArgs = { id, data };
      return Promise.resolve();
    };
    fixture.detectChanges();
    component.name.set('Updated Name');
    fixture.detectChanges();

    component.handleSave();
    await fixture.whenStable();

    expect(updateCalled).toBe(true);
    expect(updateArgs.id).toBe('1');
    expect(updateArgs.data.name).toBe('Updated Name');
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
    let modalOpenCalled = false;
    (modal as any).open = () => {
      modalOpenCalled = true;
      return of({ confirmed: false });
    };
    fixture.detectChanges();
    component.handleDeleteClick();
    expect(modalOpenCalled).toBe(true);
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
    let loadMembersCalled = false;
    (membersService as any).loadMembers = (id: string) => {
      loadMembersCalled = true;
    };
    component.handleMembersRetry();
    expect(loadMembersCalled).toBe(true);
  });

  it('should open add member modal when add member is clicked', () => {
    let modalOpenCalled = false;
    (modal as any).open = () => {
      modalOpenCalled = true;
      return of({ added: false });
    };
    fixture.detectChanges();
    component.handleAddMember();
    expect(modalOpenCalled).toBe(true);
  });

  it('should open change role modal when change role is clicked', () => {
    let modalOpenCalled = false;
    (modal as any).open = () => {
      modalOpenCalled = true;
      return of({ changed: false });
    };
    fixture.detectChanges();
    component.handleChangeRole(mockMembers[0]);
    expect(modalOpenCalled).toBe(true);
  });

  it('should call removeMember when remove member is clicked', async () => {
    let removeMemberCalled = false;
    (membersService as any).removeMember = (orgId: string, userId: string) => {
      removeMemberCalled = true;
      return Promise.resolve();
    };
    fixture.detectChanges();
    await component.handleRemoveMember(mockMembers[0]);
    expect(removeMemberCalled).toBe(true);
  });

  it('should open invite modal when send invitation is clicked', () => {
    let modalOpenCalled = false;
    (modal as any).open = () => {
      modalOpenCalled = true;
      return of({ sent: false });
    };
    fixture.detectChanges();
    component.handleSendInvitation();
    expect(modalOpenCalled).toBe(true);
  });

  it('should call cancelInvitation when cancel invitation is clicked', async () => {
    let cancelInvitationCalled = false;
    const mockInvitation: OrganizationInvitation = {
      id: '1',
      email: 'test@example.com',
      role: 'member',
      expires_at: '2024-12-31T00:00:00Z',
      created_at: '2024-01-01T00:00:00Z',
    };
    (invitationsService as any).cancelInvitation = (id: string) => {
      cancelInvitationCalled = true;
      return Promise.resolve();
    };
    fixture.detectChanges();
    await component.handleCancelInvitation(mockInvitation);
    expect(cancelInvitationCalled).toBe(true);
  });

  it('should compute organizationId from route params', () => {
    fixture.detectChanges();
    expect(component.organizationId()).toBe('1');
  });
});
