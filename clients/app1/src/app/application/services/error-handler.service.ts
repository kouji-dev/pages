import { Injectable, inject } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { ToastService } from 'shared-ui';

/**
 * Error Handler Service
 * Provides centralized error handling with user-friendly messages
 */
@Injectable({
  providedIn: 'root',
})
export class ErrorHandlerService {
  private readonly toastService = inject(ToastService);

  /**
   * Handle HTTP error and show user-friendly message
   */
  handleError(error: HttpErrorResponse, customMessage?: string): void {
    const message = customMessage || this.extractErrorMessage(error);
    this.toastService.error(message);
  }

  /**
   * Extract error message from HTTP error response
   */
  extractErrorMessage(error: HttpErrorResponse): string {
    // Try to extract message from error response body
    if (error.error) {
      // Check for nested error message
      if (typeof error.error === 'object') {
        if (error.error.message) {
          return error.error.message;
        }
        if (error.error.detail) {
          return error.error.detail;
        }
        if (error.error.error) {
          return error.error.error;
        }
      }
      // If error.error is a string
      if (typeof error.error === 'string') {
        return error.error;
      }
    }

    // Fallback to status text or default message
    if (error.statusText) {
      return error.statusText;
    }

    // Default message based on status code
    switch (error.status) {
      case 0:
        return 'Network error. Please check your connection.';
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'Authentication failed. Please log in again.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 409:
        return 'A conflict occurred. The resource may already exist.';
      case 422:
        return 'Validation error. Please check your input.';
      case 500:
        return 'Server error. Please try again later.';
      case 502:
        return 'Bad gateway. The server is temporarily unavailable.';
      case 503:
        return 'Service unavailable. Please try again later.';
      default:
        return 'An unexpected error occurred. Please try again.';
    }
  }

  /**
   * Show success message
   */
  showSuccess(message: string): void {
    this.toastService.success(message);
  }

  /**
   * Show warning message
   */
  showWarning(message: string): void {
    this.toastService.warning(message);
  }

  /**
   * Show info message
   */
  showInfo(message: string): void {
    this.toastService.info(message);
  }
}
