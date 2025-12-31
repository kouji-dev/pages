import { TestBed } from '@angular/core/testing';
import { HttpRequest, HttpErrorResponse } from '@angular/common/http';
import { of, throwError } from 'rxjs';
import { errorInterceptor } from './error.interceptor';
import { AuthService } from '../../auth/auth.service';
import { ErrorHandlerService } from '../../error-handling/error-handler.service';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('errorInterceptor', () => {
  let authService: any;
  let errorHandler: any;
  let next: any;

  beforeEach(() => {
    authService = {
      clearTokens: vi.fn(),
      logout: vi.fn(),
    };
    errorHandler = {
      handleError: vi.fn(),
    };
    next = {
      handle: vi.fn(),
    };

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: ErrorHandlerService, useValue: errorHandler },
      ],
    });

    authService = TestBed.inject(AuthService);
    errorHandler = TestBed.inject(ErrorHandlerService);
  });

  it('should handle 401 error and logout user for non-auth endpoints', () => {
    // Arrange
    const request = new HttpRequest('GET', '/api/v1/organizations');
    const error = new HttpErrorResponse({ status: 401, statusText: 'Unauthorized' });
    next.handle.mockReturnValue(throwError(() => error));

    // Act
    TestBed.runInInjectionContext(() => {
      errorInterceptor(request, next.handle).subscribe({
        error: () => {
          // Expected to throw
        },
      });
    });

    // Assert
    expect(authService.clearTokens).toHaveBeenCalled();
    expect(authService.logout).toHaveBeenCalled();
    expect(errorHandler.handleError).toHaveBeenCalled();
  });

  it('should not logout for 401 on auth endpoints', () => {
    // Arrange
    const request = new HttpRequest('POST' as any, '/api/v1/auth/login');
    const error = new HttpErrorResponse({ status: 401, statusText: 'Unauthorized' });
    next.handle.mockReturnValue(throwError(() => error));

    // Act
    TestBed.runInInjectionContext(() => {
      errorInterceptor(request, next.handle).subscribe({
        error: () => {
          // Expected to throw
        },
      });
    });

    // Assert
    expect(authService.logout).not.toHaveBeenCalled();
    expect(errorHandler.handleError).toHaveBeenCalled();
  });

  it('should handle 403 error', () => {
    // Arrange
    const request = new HttpRequest('GET', '/api/v1/organizations');
    const error = new HttpErrorResponse({ status: 403, statusText: 'Forbidden' });
    next.handle.mockReturnValue(throwError(() => error));

    // Act
    TestBed.runInInjectionContext(() => {
      errorInterceptor(request, next.handle).subscribe({
        error: () => {
          // Expected to throw
        },
      });
    });

    // Assert
    expect(errorHandler.handleError).toHaveBeenCalled();
  });

  it('should handle 500 error', () => {
    // Arrange
    const request = new HttpRequest('GET', '/api/v1/organizations');
    const error = new HttpErrorResponse({ status: 500, statusText: 'Internal Server Error' });
    next.handle.mockReturnValue(throwError(() => error));

    // Act
    TestBed.runInInjectionContext(() => {
      errorInterceptor(request, next.handle).subscribe({
        error: () => {
          // Expected to throw
        },
      });
    });

    // Assert
    expect(errorHandler.handleError).toHaveBeenCalled();
  });

  it('should pass through successful responses', () => {
    // Arrange
    const request = new HttpRequest('GET', '/api/v1/organizations');
    const response = { status: 200, body: {} };
    next.handle.mockReturnValue(of(response));

    // Act
    TestBed.runInInjectionContext(() => {
      errorInterceptor(request, next.handle).subscribe();
    });

    // Assert
    expect(errorHandler.handleError).not.toHaveBeenCalled();
  });
});
