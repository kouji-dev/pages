import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { signal, computed } from '@angular/core';
import { OrganizationsPage } from './organizations-page';
import { OrganizationService, Organization } from '../../application/services/organization.service';
import { Modal } from 'shared-ui';
import { Button, LoadingState, ErrorState, EmptyState } from 'shared-ui';
import { ViewContainerRef } from '@angular/core';

describe('OrganizationsPage', () => {
  let component: OrganizationsPage;
  let fixture: ComponentFixture<OrganizationsPage>;
  let organizationService: OrganizationService;
  let router: Router;
  let modal: Modal;
  let element: HTMLElement;

  const mockOrganizations: Organization[] = [
    {
      id: '1',
      name: 'Test Org 1',
      slug: 'test-org-1',
      description: 'Test organization 1',
      memberCount: 5,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    },
    {
      id: '2',
      name: 'Test Org 2',
      slug: 'test-org-2',
      description: 'Test organization 2',
      memberCount: 10,
      createdAt: '2024-01-02T00:00:00Z',
      updatedAt: '2024-01-02T00:00:00Z',
    },
  ];

  beforeEach(async () => {
    const mockOrganizationService = {
      organizationsList: signal<Organization[]>(mockOrganizations),
      isLoading: computed(() => false),
      error: computed(() => undefined),
      hasError: computed(() => false),
      loadOrganizations: () => {},
    };

    const mockRouter = {
      navigate: () => Promise.resolve(true),
    };

    const mockModal = {
      open: () => ({
        subscribe: () => {},
      }),
    };

    await TestBed.configureTestingModule({
      imports: [OrganizationsPage, Button, LoadingState, ErrorState, EmptyState],
      providers: [
        { provide: OrganizationService, useValue: mockOrganizationService },
        { provide: Router, useValue: mockRouter },
        { provide: Modal, useValue: mockModal },
        ViewContainerRef,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(OrganizationsPage);
    component = fixture.componentInstance;
    organizationService = TestBed.inject(OrganizationService);
    router = TestBed.inject(Router);
    modal = TestBed.inject(Modal);
    element = fixture.nativeElement;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display page title and subtitle', () => {
    fixture.detectChanges();
    const title = element.querySelector('.organizations-page_title');
    const subtitle = element.querySelector('.organizations-page_subtitle');
    expect(title?.textContent?.trim()).toBe('Organizations');
    expect(subtitle?.textContent?.trim()).toContain('Manage your organizations');
  });

  it('should display create organization button', () => {
    fixture.detectChanges();
    const createButton = element.querySelector('lib-button');
    expect(createButton).toBeTruthy();
    expect(createButton?.textContent?.trim()).toContain('Create Organization');
  });

  it('should display loading state when loading', () => {
    Object.defineProperty(organizationService, 'isLoading', {
      get: () => computed(() => true),
      configurable: true,
    });
    fixture.detectChanges();
    const loadingState = element.querySelector('lib-loading-state');
    expect(loadingState).toBeTruthy();
  });

  it('should display error state when there is an error', () => {
    Object.defineProperty(organizationService, 'hasError', {
      get: () => computed(() => true),
      configurable: true,
    });
    Object.defineProperty(organizationService, 'error', {
      get: () => computed(() => new Error('Test error')),
      configurable: true,
    });
    fixture.detectChanges();
    const errorState = element.querySelector('lib-error-state');
    expect(errorState).toBeTruthy();
  });

  it('should display empty state when no organizations', () => {
    Object.defineProperty(organizationService, 'organizationsList', {
      get: () => signal<Organization[]>([]),
      configurable: true,
    });
    Object.defineProperty(organizationService, 'isLoading', {
      get: () => computed(() => false),
      configurable: true,
    });
    Object.defineProperty(organizationService, 'hasError', {
      get: () => computed(() => false),
      configurable: true,
    });
    fixture.detectChanges();
    const emptyState = element.querySelector('lib-empty-state');
    expect(emptyState).toBeTruthy();
  });

  it('should display organizations grid when organizations exist', () => {
    fixture.detectChanges();
    const grid = element.querySelector('.organizations-page_grid');
    expect(grid).toBeTruthy();
  });

  it('should display organization cards for each organization', () => {
    fixture.detectChanges();
    const cards = element.querySelectorAll('app-organization-card');
    expect(cards.length).toBe(2);
  });

  it('should call loadOrganizations on init', () => {
    let loadOrganizationsCalled = false;
    (organizationService as any).loadOrganizations = () => {
      loadOrganizationsCalled = true;
    };
    component.ngOnInit();
    expect(loadOrganizationsCalled).toBe(true);
  });

  it('should open create organization modal when create button is clicked', () => {
    let modalOpenCalled = false;
    (modal as any).open = () => {
      modalOpenCalled = true;
      return {
        subscribe: () => {},
      };
    };
    fixture.detectChanges();
    component.handleCreateOrganization();
    expect(modalOpenCalled).toBe(true);
  });

  it('should navigate to organization settings when settings is clicked', () => {
    let navigateCalled = false;
    let navigatePath: any[] = [];
    (router as any).navigate = (path: any[]) => {
      navigateCalled = true;
      navigatePath = path;
      return Promise.resolve(true);
    };
    const org = mockOrganizations[0];
    component.handleOrganizationSettings(org);
    expect(navigateCalled).toBe(true);
    expect(navigatePath).toEqual(['/app/organizations', org.id, 'settings']);
  });

  it('should call loadOrganizations when retry is clicked', () => {
    let loadOrganizationsCalled = false;
    (organizationService as any).loadOrganizations = () => {
      loadOrganizationsCalled = true;
    };
    component.handleRetry();
    expect(loadOrganizationsCalled).toBe(true);
  });

  it('should compute organizations list from service', () => {
    fixture.detectChanges();
    expect(component.organizations().length).toBe(2);
    expect(component.organizations()[0].name).toBe('Test Org 1');
  });

  it('should compute error message from service error', () => {
    Object.defineProperty(organizationService, 'error', {
      get: () => computed(() => new Error('Test error message')),
      configurable: true,
    });
    fixture.detectChanges();
    expect(component.errorMessage()).toBe('Test error message');
  });

  it('should handle empty organizations list', () => {
    Object.defineProperty(organizationService, 'organizationsList', {
      get: () => signal<Organization[]>([]),
      configurable: true,
    });
    Object.defineProperty(organizationService, 'isLoading', {
      get: () => computed(() => false),
      configurable: true,
    });
    Object.defineProperty(organizationService, 'hasError', {
      get: () => computed(() => false),
      configurable: true,
    });
    fixture.detectChanges();
    expect(component.organizations().length).toBe(0);
  });
});
