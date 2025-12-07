import { ComponentFixture, TestBed } from '@angular/core/testing';
import { InviteMemberModal } from './invite-member-modal';
import { OrganizationInvitationsService } from '../../application/services/organization-invitations.service';
import { Modal, ToastService } from 'shared-ui';
import { ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input } from 'shared-ui';

describe('InviteMemberModal', () => {
  let component: InviteMemberModal;
  let fixture: ComponentFixture<InviteMemberModal>;
  let invitationsService: OrganizationInvitationsService;
  let modal: Modal;
  let toastService: ToastService;
  let element: HTMLElement;

  beforeEach(async () => {
    const mockInvitationsService = {
      sendInvitation: () => Promise.resolve(),
    };

    const mockModal = {
      close: () => {},
    };

    const mockToastService = {
      success: () => {},
      error: () => {},
    };

    await TestBed.configureTestingModule({
      imports: [
        InviteMemberModal,
        ModalContainer,
        ModalHeader,
        ModalContent,
        ModalFooter,
        Button,
        Input,
      ],
      providers: [
        { provide: OrganizationInvitationsService, useValue: mockInvitationsService },
        { provide: Modal, useValue: mockModal },
        { provide: ToastService, useValue: mockToastService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(InviteMemberModal);
    component = fixture.componentInstance;
    invitationsService = TestBed.inject(OrganizationInvitationsService);
    modal = TestBed.inject(Modal);
    toastService = TestBed.inject(ToastService);
    element = fixture.nativeElement;
    fixture.componentRef.setInput('organizationId', 'org1');
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display modal header', () => {
    fixture.detectChanges();
    const header = element.querySelector('lib-modal-header');
    expect(header?.textContent?.trim()).toBe('Send Invitation');
  });

  it('should display email input', () => {
    fixture.detectChanges();
    const emailInput = element.querySelector('lib-input[label="Email Address"]');
    expect(emailInput).toBeTruthy();
  });

  it('should display role selection options', () => {
    fixture.detectChanges();
    const roleOptions = element.querySelectorAll('.invite-member-form_role-option');
    expect(roleOptions.length).toBe(3); // admin, member, viewer
  });

  it('should have default role as member', () => {
    fixture.detectChanges();
    expect(component.selectedRole()).toBe('member');
  });

  it('should validate email - required', () => {
    fixture.detectChanges();
    component.email.set('');
    fixture.detectChanges();
    expect(component.emailError()).toBe('Email address is required');
    expect(component.isValid()).toBe(false);
  });

  it('should validate email - format', () => {
    fixture.detectChanges();
    component.email.set('invalid-email');
    fixture.detectChanges();
    expect(component.emailError()).toBe('Please enter a valid email address');
    expect(component.isValid()).toBe(false);
  });

  it('should validate email - valid', () => {
    fixture.detectChanges();
    component.email.set('test@example.com');
    fixture.detectChanges();
    expect(component.emailError()).toBe('');
    expect(component.isValid()).toBe(true);
  });

  it('should select role when role option is clicked', () => {
    fixture.detectChanges();
    component.selectedRole.set('admin');
    fixture.detectChanges();
    expect(component.selectedRole()).toBe('admin');
  });

  it('should compute available roles', () => {
    fixture.detectChanges();
    const roles = component.availableRoles();
    expect(roles.length).toBe(3);
    expect(roles[0].value).toBe('admin');
    expect(roles[1].value).toBe('member');
    expect(roles[2].value).toBe('viewer');
  });

  it('should call sendInvitation when form is submitted', async () => {
    let sendInvitationCalled = false;
    let sendInvitationArgs: any = null;
    (invitationsService as any).sendInvitation = (orgId: string, request: any) => {
      sendInvitationCalled = true;
      sendInvitationArgs = { orgId, request };
      return Promise.resolve();
    };
    fixture.detectChanges();
    component.email.set('test@example.com');
    component.selectedRole.set('admin');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(sendInvitationCalled).toBe(true);
    expect(sendInvitationArgs.orgId).toBe('org1');
    expect(sendInvitationArgs.request.email).toBe('test@example.com');
    expect(sendInvitationArgs.request.role).toBe('admin');
  });

  it('should show success toast after successful submission', async () => {
    let successCalled = false;
    let successMessage = '';
    (invitationsService as any).sendInvitation = () => Promise.resolve();
    (toastService as any).success = (message: string) => {
      successCalled = true;
      successMessage = message;
    };
    fixture.detectChanges();
    component.email.set('test@example.com');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(successCalled).toBe(true);
    expect(successMessage).toBe('Invitation sent successfully!');
  });

  it('should close modal with sent flag after successful submission', async () => {
    let modalCloseCalled = false;
    let modalClosePayload: any = null;
    (invitationsService as any).sendInvitation = () => Promise.resolve();
    (modal as any).close = (payload: any) => {
      modalCloseCalled = true;
      modalClosePayload = payload;
    };
    fixture.detectChanges();
    component.email.set('test@example.com');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(modalCloseCalled).toBe(true);
    expect(modalClosePayload?.sent).toBe(true);
  });

  it('should show error toast when submission fails', async () => {
    const error = new Error('Test error');
    let errorCalled = false;
    let errorMessage = '';
    (invitationsService as any).sendInvitation = () => Promise.reject(error);
    (toastService as any).error = (message: string) => {
      errorCalled = true;
      errorMessage = message;
    };
    fixture.detectChanges();
    component.email.set('test@example.com');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(errorCalled).toBe(true);
    expect(errorMessage).toBe('Test error');
  });

  it('should close modal when cancel is clicked', () => {
    let modalCloseCalled = false;
    (modal as any).close = () => {
      modalCloseCalled = true;
    };
    fixture.detectChanges();
    component.handleCancel();
    expect(modalCloseCalled).toBe(true);
  });

  it('should not submit when form is invalid', async () => {
    let sendInvitationCalled = false;
    (invitationsService as any).sendInvitation = () => {
      sendInvitationCalled = true;
      return Promise.resolve();
    };
    fixture.detectChanges();
    component.email.set('');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(sendInvitationCalled).toBe(false);
  });

  it('should disable submit button when form is invalid', () => {
    fixture.detectChanges();
    component.email.set('');
    fixture.detectChanges();
    const submitButton = element.querySelector('lib-button[variant="primary"]');
    expect(submitButton?.getAttribute('ng-reflect-disabled')).toBe('true');
  });

  it('should enable submit button when form is valid', () => {
    fixture.detectChanges();
    component.email.set('test@example.com');
    fixture.detectChanges();
    const submitButton = element.querySelector('lib-button[variant="primary"]');
    expect(submitButton?.getAttribute('ng-reflect-disabled')).toBe('false');
  });
});
