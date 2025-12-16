import { ComponentFixture, TestBed } from '@angular/core/testing';
import { InviteMemberModal } from './invite-member-modal.component';
import { OrganizationInvitationsService } from '../../../../application/services/organization-invitations.service';
import { Modal, ToastService } from 'shared-ui';
import { ModalContainer, ModalHeader, ModalContent, ModalFooter, Button, Input } from 'shared-ui';
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('InviteMemberModal', () => {
  let component: InviteMemberModal;
  let fixture: ComponentFixture<InviteMemberModal>;
  let invitationsService: OrganizationInvitationsService;
  let modal: Modal;
  let toastService: ToastService;
  let element: HTMLElement;

  beforeEach(async () => {
    const mockInvitationsService = {
      sendInvitation: vi.fn().mockResolvedValue(undefined),
    };

    const mockModal = {
      close: vi.fn(),
    };

    const mockToastService = {
      success: vi.fn(),
      error: vi.fn(),
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
    expect(header?.textContent?.trim()).toBe('invitations.title');
  });

  it('should display email input', () => {
    fixture.detectChanges();
    const emailInput = element.querySelector('lib-input');
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
    expect(component.emailError()).toBe('invitations.emailRequired');
    expect(component.isValid()).toBe(false);
  });

  it('should validate email - format', () => {
    fixture.detectChanges();
    component.email.set('invalid-email');
    fixture.detectChanges();
    expect(component.emailError()).toBe('invitations.emailInvalid');
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
    fixture.detectChanges();
    component.email.set('test@example.com');
    component.selectedRole.set('admin');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(invitationsService.sendInvitation).toHaveBeenCalledWith('org1', {
      email: 'test@example.com',
      role: 'admin',
    });
  });

  it('should show success toast after successful submission', async () => {
    fixture.detectChanges();
    component.email.set('test@example.com');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(toastService.success).toHaveBeenCalledWith('invitations.invitationSent');
  });

  it('should close modal with sent flag after successful submission', async () => {
    fixture.detectChanges();
    component.email.set('test@example.com');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(modal.close).toHaveBeenCalledWith({ sent: true });
  });

  it('should show error toast when submission fails', async () => {
    const error = new Error('Test error');
    vi.mocked(invitationsService.sendInvitation).mockRejectedValue(error);

    fixture.detectChanges();
    component.email.set('test@example.com');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(toastService.error).toHaveBeenCalledWith('Test error');
  });

  it('should close modal when cancel is clicked', () => {
    fixture.detectChanges();
    component.handleCancel();
    expect(modal.close).toHaveBeenCalled();
  });

  it('should not submit when form is invalid', async () => {
    fixture.detectChanges();
    component.email.set('');
    fixture.detectChanges();

    await component.handleSubmit();

    expect(invitationsService.sendInvitation).not.toHaveBeenCalled();
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
