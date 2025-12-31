import { TestBed } from '@angular/core/testing';
import { HttpRequest, HttpHandler } from '@angular/common/http';
import { of } from 'rxjs';
import { authInterceptor } from './auth.interceptor';
import { AuthService } from '../../auth/auth.service';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('authInterceptor', () => {
  let authService: any;
  let next: any;

  beforeEach(() => {
    authService = {
      getAccessToken: vi.fn(),
      getRefreshToken: vi.fn(),
      refreshToken: vi.fn(),
    };
    next = {
      handle: vi.fn(),
    };

    TestBed.configureTestingModule({
      providers: [{ provide: AuthService, useValue: authService }],
    });

    authService = TestBed.inject(AuthService);
  });

  it('should add Authorization header when token exists', () => {
    // Arrange
    const request = new HttpRequest('GET', '/api/v1/organizations');
    authService.getAccessToken.mockReturnValue('test-token');
    next.handle.mockReturnValue(of({} as any));

    // Act
    TestBed.runInInjectionContext(() => {
      authInterceptor(request, next.handle).subscribe();
    });

    // Assert
    expect(next.handle).toHaveBeenCalled();
    const interceptedRequest = next.handle.mock.calls[0][0] as HttpRequest<unknown>;
    expect(interceptedRequest.headers.get('Authorization')).toBe('Bearer test-token');
  });

  it('should not add token for auth endpoints', () => {
    // Arrange
    const request = new HttpRequest('POST' as any, '/api/v1/auth/login');
    next.handle.mockReturnValue(of({} as any));

    // Act
    TestBed.runInInjectionContext(() => {
      authInterceptor(request, next.handle).subscribe();
    });

    // Assert
    expect(next.handle).toHaveBeenCalled();
    const interceptedRequest = next.handle.mock.calls[0][0] as HttpRequest<unknown>;
    expect(interceptedRequest.headers.has('Authorization')).toBe(false);
  });

  it('should not add token for non-API requests', () => {
    // Arrange
    const request = new HttpRequest('GET', '/assets/logo.png');
    next.handle.mockReturnValue(of({} as any));

    // Act
    TestBed.runInInjectionContext(() => {
      authInterceptor(request, next.handle).subscribe();
    });

    // Assert
    expect(next.handle).toHaveBeenCalled();
    const interceptedRequest = next.handle.mock.calls[0][0] as HttpRequest<unknown>;
    expect(interceptedRequest.headers.has('Authorization')).toBe(false);
  });

  it('should proceed without token if no token exists', () => {
    // Arrange
    const request = new HttpRequest('GET', '/api/v1/organizations');
    authService.getAccessToken.mockReturnValue(null);
    next.handle.mockReturnValue(of({} as any));

    // Act
    TestBed.runInInjectionContext(() => {
      authInterceptor(request, next.handle).subscribe();
    });

    // Assert
    expect(next.handle).toHaveBeenCalled();
    const interceptedRequest = next.handle.mock.calls[0][0] as HttpRequest<unknown>;
    expect(interceptedRequest.headers.has('Authorization')).toBe(false);
  });
});
