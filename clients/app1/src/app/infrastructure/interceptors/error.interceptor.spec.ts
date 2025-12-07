import { TestBed } from '@angular/core/testing';
import { HttpRequest, HttpErrorResponse } from '@angular/common/http';
import { of, throwError } from 'rxjs';
import { errorInterceptor } from './error.interceptor';
import { AuthService } from '../../application/services/auth.service';
import { ErrorHandlerService } from '../../application/services/error-handler.service';

describe('errorInterceptor', () => {
  let authService: jasmine.SpyObj<AuthService>;
  let errorHandler: jasmine.SpyObj<ErrorHandlerService>;
  let next: jasmine.SpyObj<any>;

  beforeEach(() => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['clearTokens', 'logout']);
    const errorHandlerSpy = jasmine.createSpyObj('ErrorHandlerService', ['handleError']);
    const nextSpy = jasmine.createSpyObj('HttpHandler', ['handle']);

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authServiceSpy },
        { provide: ErrorHandlerService, useValue: errorHandlerSpy },
      ],
    });

    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    errorHandler = TestBed.inject(ErrorHandlerService) as jasmine.SpyObj<ErrorHandlerService>;
    next = nextSpy;
  });

  it('should handle 401 error and logout user for non-auth endpoints', () => {
    // Arrange
    const request = new HttpRequest('GET', '/api/v1/organizations');
    const error = new HttpErrorResponse({ status: 401, statusText: 'Unauthorized' });
    next.handle.and.returnValue(throwError(() => error));

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
    const request = new HttpRequest('POST', '/api/v1/auth/login');
    const error = new HttpErrorResponse({ status: 401, statusText: 'Unauthorized' });
    next.handle.and.returnValue(throwError(() => error));

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
    next.handle.and.returnValue(throwError(() => error));

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
    next.handle.and.returnValue(throwError(() => error));

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
    next.handle.and.returnValue(of(response));

    // Act
    TestBed.runInInjectionContext(() => {
      errorInterceptor(request, next.handle).subscribe();
    });

    // Assert
    expect(errorHandler.handleError).not.toHaveBeenCalled();
  });
});
