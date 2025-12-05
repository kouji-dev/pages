import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CreateOrganizationModal } from './create-organization-modal';
import { OrganizationService } from '../../application/services/organization.service';
import { Modal } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { Router } from '@angular/router';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { signal } from '@angular/core';

describe('CreateOrganizationModal', () => {
  let component: CreateOrganizationModal;
  let fixture: ComponentFixture<CreateOrganizationModal>;
  let organizationService: jasmine.SpyObj<OrganizationService>;
  let modalService: jasmine.SpyObj<Modal>;
  let toastService: jasmine.SpyObj<ToastService>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    const orgServiceSpy = jasmine.createSpyObj('OrganizationService', [
      'createOrganization',
      'loadOrganizations',
      'switchOrganization',
    ]);
    const modalSpy = jasmine.createSpyObj('Modal', ['close']);
    const toastSpy = jasmine.createSpyObj('ToastService', ['success', 'error']);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      imports: [CreateOrganizationModal, BrowserAnimationsModule],
      providers: [
        { provide: OrganizationService, useValue: orgServiceSpy },
        { provide: Modal, useValue: modalSpy },
        { provide: ToastService, useValue: toastSpy },
        { provide: Router, useValue: routerSpy },
      ],
    }).compileComponents();

    organizationService = TestBed.inject(
      OrganizationService,
    ) as jasmine.SpyObj<OrganizationService>;
    modalService = TestBed.inject(Modal) as jasmine.SpyObj<Modal>;
    toastService = TestBed.inject(ToastService) as jasmine.SpyObj<ToastService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;

    fixture = TestBed.createComponent(CreateOrganizationModal);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should validate organization name', () => {
    component.name.set('');
    fixture.detectChanges();
    expect(component.nameError()).toBe('Organization name is required');

    component.name.set('ab');
    fixture.detectChanges();
    expect(component.nameError()).toBe('Organization name must be at least 3 characters');

    component.name.set('Valid Name');
    fixture.detectChanges();
    expect(component.nameError()).toBe('');
  });

  it('should validate slug format', () => {
    component.slug.set('');
    fixture.detectChanges();
    expect(component.slugError()).toBe('Slug is required');

    component.slug.set('ab');
    fixture.detectChanges();
    expect(component.slugError()).toBe('Slug must be at least 3 characters');

    component.slug.set('INVALID_SLUG');
    fixture.detectChanges();
    expect(component.slugError()).toBe(
      'Slug can only contain lowercase letters, numbers, and hyphens',
    );

    component.slug.set('valid-slug-123');
    fixture.detectChanges();
    expect(component.slugError()).toBe('');
  });

  it('should auto-generate slug from name', (done) => {
    component.name.set('My Organization');
    fixture.detectChanges();

    setTimeout(() => {
      expect(component.slug()).toBe('my-organization');
      done();
    }, 100);
  });

  it('should not auto-generate slug if manually edited', (done) => {
    component.slug.set('custom-slug');
    component.name.set('New Organization Name');
    fixture.detectChanges();

    setTimeout(() => {
      // Slug should remain custom if manually edited
      expect(component.slug()).toBe('custom-slug');
      done();
    }, 100);
  });

  it('should call createOrganization on submit', async () => {
    const mockOrg = {
      id: 'org-1',
      name: 'Test Org',
      slug: 'test-org',
      description: 'Test',
    };

    organizationService.createOrganization.and.returnValue(Promise.resolve(mockOrg));
    organizationService.loadOrganizations.and.returnValue(undefined);

    component.name.set('Test Org');
    component.slug.set('test-org');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(organizationService.createOrganization).toHaveBeenCalledWith({
      name: 'Test Org',
      slug: 'test-org',
      description: undefined,
    });
    expect(toastService.success).toHaveBeenCalledWith('Organization created successfully!');
    expect(modalService.close).toHaveBeenCalled();
  });

  it('should not submit if form is invalid', async () => {
    component.name.set('');
    component.slug.set('');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(organizationService.createOrganization).not.toHaveBeenCalled();
  });

  it('should handle errors on submit', async () => {
    organizationService.createOrganization.and.returnValue(Promise.reject(new Error('API Error')));

    component.name.set('Test Org');
    component.slug.set('test-org');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(toastService.error).toHaveBeenCalledWith(
      'Failed to create organization. Please try again.',
    );
  });
});
