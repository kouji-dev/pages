import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { CreateOrganizationModal } from './create-organization-modal';
import { OrganizationService } from '../../../../application/services/organization.service';
import { Modal } from 'shared-ui';
import { ToastService } from 'shared-ui';
import { Router } from '@angular/router';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('CreateOrganizationModal', () => {
  let component: CreateOrganizationModal;
  let fixture: ComponentFixture<CreateOrganizationModal>;
  let organizationService: any;
  let modalService: any;
  let toastService: any;
  let router: any;

  beforeEach(async () => {
    organizationService = {
      createOrganization: vi.fn(),
      loadOrganizations: vi.fn(),
      switchOrganization: vi.fn(),
    };
    modalService = {
      close: vi.fn(),
    };
    toastService = {
      success: vi.fn(),
      error: vi.fn(),
    };
    router = {
      navigate: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [CreateOrganizationModal, BrowserAnimationsModule],
      providers: [
        { provide: OrganizationService, useValue: organizationService },
        { provide: Modal, useValue: modalService },
        { provide: ToastService, useValue: toastService },
        { provide: Router, useValue: router },
      ],
    }).compileComponents();

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
    expect(component.nameError()).toBe('organizations.modals.nameRequired'); // Using translation key or mock return

    component.name.set('ab');
    fixture.detectChanges();
    expect(component.nameError()).toBe('organizations.modals.nameMinLength');

    component.name.set('Valid Name');
    fixture.detectChanges();
    expect(component.nameError()).toBe('');
  });

  it('should validate slug format', () => {
    component.slug.set('');
    fixture.detectChanges();
    expect(component.slugError()).toBe('organizations.modals.slugRequired');

    component.slug.set('ab');
    fixture.detectChanges();
    expect(component.slugError()).toBe('organizations.modals.slugMinLength');

    component.slug.set('INVALID_SLUG');
    fixture.detectChanges();
    expect(component.slugError()).toBe('organizations.modals.slugInvalidFormat');

    component.slug.set('valid-slug-123');
    fixture.detectChanges();
    expect(component.slugError()).toBe('');
  });

  it('should auto-generate slug from name', () => {
    // Effects run asynchronously or on change detection.
    // We might need to trigger change detection or wait.
    return new Promise<void>((resolve) => {
      component.name.set('My Organization');
      fixture.detectChanges();

      setTimeout(() => {
        expect(component.slug()).toBe('my-organization');
        resolve();
      }, 100);
    });
  });

  it('should not auto-generate slug if manually edited', () => {
    return new Promise<void>((resolve) => {
      component.slug.set('custom-slug');
      component.name.set('New Organization Name');
      fixture.detectChanges();

      setTimeout(() => {
        expect(component.slug()).toBe('custom-slug');
        resolve();
      }, 100);
    });
  });

  it('should call createOrganization on submit', async () => {
    const mockOrg = {
      id: 'org-1',
      name: 'Test Org',
      slug: 'test-org',
      description: 'Test',
    };

    organizationService.createOrganization.mockResolvedValue(mockOrg);
    organizationService.loadOrganizations.mockReturnValue(undefined);

    component.name.set('Test Org');
    component.slug.set('test-org');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(organizationService.createOrganization).toHaveBeenCalledWith({
      name: 'Test Org',
      slug: 'test-org',
      description: undefined,
    });
    // TranslateService is mocked/stubbed implicitly or returns keys effectively in tests usually,
    // or we check calls. Here we just expect specific calls.
    expect(toastService.success).toHaveBeenCalled();
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
    organizationService.createOrganization.mockRejectedValue(new Error('API Error'));

    component.name.set('Test Org');
    component.slug.set('test-org');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(toastService.error).toHaveBeenCalled();
  });
});
