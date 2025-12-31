import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { signal, computed, ViewContainerRef, Component } from '@angular/core';
import { of } from 'rxjs';
import { InvitationAcceptancePage } from './invitation-acceptance-page.component';
import { AuthService } from '../../../../core/auth/auth.service';
import { OrganizationInvitationsService } from '../../../../application/services/organization-invitations.service';
import { ToastService, Button, Icon, LoadingState, ErrorState } from 'shared-ui';
import { PublicNav } from '../../../../presentation/components/public-nav';
import { Footer } from '../../../../presentation/components/footer';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { TranslateModule } from '@ngx-translate/core';

// Mock components
@Component({ selector: 'app-public-nav', template: '', standalone: true })
class MockPublicNav {}

@Component({ selector: 'app-footer', template: '', standalone: true })
class MockFooter {}

describe('InvitationAcceptancePage', () => {
  let component: InvitationAcceptancePage;
  let fixture: ComponentFixture<InvitationAcceptancePage>;
  let authService: AuthService;
  let invitationsService: OrganizationInvitationsService;
  let toastService: ToastService;
  let router: Router;
  let element: HTMLElement;

  let isAuthenticatedSignal: any;

  beforeEach(async () => {
    isAuthenticatedSignal = signal(false);

    const mockAuthService = {
      isAuthenticated: isAuthenticatedSignal,
      getUser: () => ({ email: 'test@test.com' }),
      currentUser: signal(null),
    };

    const mockInvitationsService = {
      acceptInvitation: vi.fn(),
    };

    const mockToastService = {
      success: vi.fn(),
      error: vi.fn(),
    };

    const mockRouter = {
      navigate: vi.fn(),
    };

    const mockActivatedRoute = {
      snapshot: {
        paramMap: {
          get: (key: string) => (key === 'token' ? 'valid-token' : null),
        },
      },
    };

    await TestBed.configureTestingModule({
      imports: [
        InvitationAcceptancePage,
        Button,
        Icon,
        LoadingState,
        ErrorState,
        TranslateModule.forRoot(),
      ],
      providers: [
        { provide: AuthService, useValue: mockAuthService },
        { provide: OrganizationInvitationsService, useValue: mockInvitationsService },
        { provide: ToastService, useValue: mockToastService },
        { provide: Router, useValue: mockRouter },
        { provide: ActivatedRoute, useValue: mockActivatedRoute },
      ],
    })
      .overrideComponent(InvitationAcceptancePage, {
        remove: { imports: [PublicNav, Footer] },
        add: { imports: [MockPublicNav, MockFooter] },
      })
      .compileComponents();

    fixture = TestBed.createComponent(InvitationAcceptancePage);
    component = fixture.componentInstance;
    authService = TestBed.inject(AuthService);
    invitationsService = TestBed.inject(OrganizationInvitationsService);
    toastService = TestBed.inject(ToastService);
    router = TestBed.inject(Router);
    element = fixture.nativeElement;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should get token from route', () => {
    expect(component.token()).toBe('valid-token');
  });

  it('should show login/register options when not authenticated', () => {
    fixture.detectChanges();
    const unauthenticated = element.querySelector('.invitation-acceptance-page_unauthenticated');
    expect(unauthenticated).toBeTruthy();
  });

  it('should navigate to login when login clicked', () => {
    fixture.detectChanges();
    component.handleLogin();
    expect(router.navigate).toHaveBeenCalledWith(
      ['/login'],
      expect.objectContaining({ queryParams: { returnUrl: '/invitations/valid-token' } }),
    );
  });

  it('should navigate to register when register clicked', () => {
    fixture.detectChanges();
    component.handleRegister();
    expect(router.navigate).toHaveBeenCalledWith(
      ['/register'],
      expect.objectContaining({ queryParams: { returnUrl: '/invitations/valid-token' } }),
    );
  });

  it('should show accept button when authenticated', () => {
    // Need to re-create component or update signal if possible.
    // Signals are read-only if exposed as such, but here we mocked the service which has the signal.
    // However, we passed signal(false) initially.
    // Let's manually trigger change? No, signals are reactive.
    // But we passed a signal to the provider.
    // We can update the signal if we kept a reference to it.
    // In the mock above: `isAuthenticated: signal(false)`.
    // But `authService` variable in test holds the mocked object.
    // The `isAuthenticated` property IS the signal.
    // Wait, `authService.isAuthenticated` is defined as a property that IS a signal in `AuthService`.
    // So `authService.isAuthenticated()` reads it.
    // In the mock, we set it to `signal(false)`.
    // We need to cast it to WritableSignal to set it.
  });

  it('should show accept button when authenticated', () => {
    isAuthenticatedSignal.set(true);
    fixture.detectChanges();
    const authenticated = element.querySelector('.invitation-acceptance-page_authenticated');
    expect(authenticated).toBeTruthy();
    const acceptBtn = element.querySelector('lib-button[leftIcon="check"]');
    expect(acceptBtn).toBeTruthy();
  });

  it('should call acceptInvitation when accept button clicked', async () => {
    isAuthenticatedSignal.set(true);
    fixture.detectChanges();
    await component.handleAccept();
    expect(invitationsService.acceptInvitation).toHaveBeenCalledWith('valid-token');
  });

  it('should show success state when invitation accepted', async () => {
    isAuthenticatedSignal.set(true);
    // Mock success return
    vi.mocked(invitationsService.acceptInvitation).mockResolvedValue({
      organization_id: '1',
      organization_name: 'Test Org',
      organization_slug: 'test-org',
      role: 'member',
      message: 'Invitation accepted successfully',
    });

    fixture.detectChanges();
    await component.handleAccept();
    fixture.detectChanges();

    const success = element.querySelector('.invitation-acceptance-page_success');
    expect(success).toBeTruthy();
  });
});
