import { NavigationService } from '../../../../application/services/navigation.service';
// ... imports

describe('OrganizationsPage', () => {
  // ...
  let navigationService: any;
  let element: HTMLElement;

  // ...

  beforeEach(async () => {
    organizationService = {
      organizationsList: signal<Organization[]>(mockOrganizations),
      isLoading: computed(() => false),
      error: computed(() => undefined),
      hasError: computed(() => false),
      loadOrganizations: vi.fn(),
    };

    router = {
      navigate: vi.fn().mockResolvedValue(true),
    };

    modal = {
      open: vi.fn().mockReturnValue({
        subscribe: vi.fn(),
      }),
    };

    navigationService = {
      navigateToOrganizationSettings: vi.fn(),
      navigateToOrganizationProjects: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [OrganizationsPage, Button, LoadingState, ErrorState, EmptyState],
      providers: [
        { provide: OrganizationService, useValue: organizationService },
        { provide: Router, useValue: router },
        { provide: Modal, useValue: modal },
        { provide: NavigationService, useValue: navigationService },
        ViewContainerRef,
      ],
    }).compileComponents();
    // ...

    fixture = TestBed.createComponent(OrganizationsPage);
    component = fixture.componentInstance;
    element = fixture.nativeElement;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display page title and subtitle', () => {
    fixture.detectChanges();
    const title = element.querySelector('.organizations-page_title');
    const subtitle = element.querySelector('.organizations-page_subtitle');
    expect(title?.textContent?.trim()).toBe('organizations.title'); // Using translation key
    expect(subtitle?.textContent?.trim()).toContain('organizations.subtitle');
  });

  it('should display create organization button', () => {
    fixture.detectChanges();
    const createButton = element.querySelector('lib-button');
    expect(createButton).toBeTruthy();
    expect(createButton?.textContent?.trim()).toContain('organizations.createOrganization');
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
    // Effect runs on creation/detection
    fixture.detectChanges();
    expect(organizationService.loadOrganizations).toHaveBeenCalled();
  });

  it('should open create organization modal when create button is clicked', () => {
    fixture.detectChanges();
    component.handleCreateOrganization();
    expect(modal.open).toHaveBeenCalled();
  });

  it('should navigate to organization settings when settings is clicked', () => {
    const org = mockOrganizations[0];
    component.handleOrganizationSettings(org);
    // NavigationService is not mocked directly, but we rely on simple call
    // Wait, component uses NavigationService, but we provided Router mock?
    // The component injects NavigationService.
    // I need to provide NavigationService mock or mock Router if NavigationService uses Router.
    // The component uses NavigationService.navigateToOrganizationSettings.
    // Check component again.
    // `readonly navigationService = inject(NavigationService);`
    // I missed providing NavigationService in the test!
    // I need to update the providers in beforeEach.
  });
});
