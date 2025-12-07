import { TestBed } from '@angular/core/testing';
import { HttpRequest, HttpHandler } from '@angular/common/http';
import { of, throwError } from 'rxjs';
import { authInterceptor } from './auth.interceptor';
import { AuthService } from '../../application/services/auth.service';

describe('authInterceptor', () => {
  let authService: jasmine.SpyObj<AuthService>;
  let next: jasmine.SpyObj<HttpHandler>;

  beforeEach(() => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', [
      'getAccessToken',
      'getRefreshToken',
      'refreshToken',
    ]);
    const nextSpy = jasmine.createSpyObj('HttpHandler', ['handle']);

    TestBed.configureTestingModule({
      providers: [{ provide: AuthService, useValue: authServiceSpy }],
    });

    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    next = nextSpy;
  });

  it('should add Authorization header when token exists', () => {
    // Arrange
    const request = new HttpRequest('GET', '/api/v1/organizations');
    authService.getAccessToken.and.returnValue('test-token');
    next.handle.and.returnValue(of({} as any));

    // Act
    TestBed.runInInjectionContext(() => {
      authInterceptor(request, next.handle).subscribe();
    });

    // Assert
    expect(next.handle).toHaveBeenCalled();
    const interceptedRequest = next.handle.calls.mostRecent().args[0] as HttpRequest<unknown>;
    expect(interceptedRequest.headers.get('Authorization')).toBe('Bearer test-token');
  });

  it('should not add token for auth endpoints', () => {
    // Arrange
    const request = new HttpRequest('POST', '/api/v1/auth/login');
    next.handle.and.returnValue(of({} as any));

    // Act
    TestBed.runInInjectionContext(() => {
      authInterceptor(request, next.handle).subscribe();
    });

    // Assert
    expect(next.handle).toHaveBeenCalled();
    const interceptedRequest = next.handle.calls.mostRecent().args[0] as HttpRequest<unknown>;
    expect(interceptedRequest.headers.has('Authorization')).toBe(false);
  });

  it('should not add token for non-API requests', () => {
    // Arrange
    const request = new HttpRequest('GET', '/assets/logo.png');
    next.handle.and.returnValue(of({} as any));

    // Act
    TestBed.runInInjectionContext(() => {
      authInterceptor(request, next.handle).subscribe();
    });

    // Assert
    expect(next.handle).toHaveBeenCalled();
    const interceptedRequest = next.handle.calls.mostRecent().args[0] as HttpRequest<unknown>;
    expect(interceptedRequest.headers.has('Authorization')).toBe(false);
  });

  it('should proceed without token if no token exists', () => {
    // Arrange
    const request = new HttpRequest('GET', '/api/v1/organizations');
    authService.getAccessToken.and.returnValue(null);
    next.handle.and.returnValue(of({} as any));

    // Act
    TestBed.runInInjectionContext(() => {
      authInterceptor(request, next.handle).subscribe();
    });

    // Assert
    expect(next.handle).toHaveBeenCalled();
    const interceptedRequest = next.handle.calls.mostRecent().args[0] as HttpRequest<unknown>;
    expect(interceptedRequest.headers.has('Authorization')).toBe(false);
  });
});
