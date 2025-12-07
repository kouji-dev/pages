import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Toast } from './toast';
import { fakeAsync, tick } from '@angular/core/testing';

describe('Toast', () => {
  let component: Toast;
  let fixture: ComponentFixture<Toast>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Toast],
    }).compileComponents();

    fixture = TestBed.createComponent(Toast);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have default type of info', () => {
    expect(component.type()).toBe('info');
  });

  it('should have default closable of true', () => {
    expect(component.closable()).toBe(true);
  });

  it('should apply success type class', () => {
    fixture.componentRef.setInput('type', 'success');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const toast = compiled.querySelector('.toast');
    expect(toast?.classList.contains('toast--success')).toBe(true);
  });

  it('should apply error type class', () => {
    fixture.componentRef.setInput('type', 'error');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const toast = compiled.querySelector('.toast');
    expect(toast?.classList.contains('toast--error')).toBe(true);
  });

  it('should apply warning type class', () => {
    fixture.componentRef.setInput('type', 'warning');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const toast = compiled.querySelector('.toast');
    expect(toast?.classList.contains('toast--warning')).toBe(true);
  });

  it('should apply info type class', () => {
    fixture.componentRef.setInput('type', 'info');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const toast = compiled.querySelector('.toast');
    expect(toast?.classList.contains('toast--info')).toBe(true);
  });

  it('should display message when provided', () => {
    fixture.componentRef.setInput('message', 'Test message');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const message = compiled.querySelector('.toast_message-text');
    expect(message?.textContent?.trim()).toBe('Test message');
  });

  it('should not display message when empty', () => {
    fixture.componentRef.setInput('message', '');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const message = compiled.querySelector('.toast_message');
    expect(message).toBeFalsy();
  });

  it('should display close button when closable is true', () => {
    fixture.componentRef.setInput('closable', true);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const closeButton = compiled.querySelector('.toast_close');
    expect(closeButton).toBeTruthy();
  });

  it('should not display close button when closable is false', () => {
    fixture.componentRef.setInput('closable', false);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const closeButton = compiled.querySelector('.toast_close');
    expect(closeButton).toBeFalsy();
  });

  it('should set correct icon for success type', fakeAsync(() => {
    fixture.componentRef.setInput('type', 'success');
    fixture.detectChanges();
    tick(20);
    expect(component.iconName()).toBe('circle-check');
  }));

  it('should set correct icon for error type', fakeAsync(() => {
    fixture.componentRef.setInput('type', 'error');
    fixture.detectChanges();
    tick(20);
    expect(component.iconName()).toBe('circle-x');
  }));

  it('should set correct icon for warning type', fakeAsync(() => {
    fixture.componentRef.setInput('type', 'warning');
    fixture.detectChanges();
    tick(20);
    expect(component.iconName()).toBe('circle-alert');
  }));

  it('should set correct icon for info type', fakeAsync(() => {
    fixture.componentRef.setInput('type', 'info');
    fixture.detectChanges();
    tick(20);
    expect(component.iconName()).toBe('info');
  }));

  it('should become visible after initialization', fakeAsync(() => {
    expect(component.isVisible()).toBe(false);
    tick(20);
    expect(component.isVisible()).toBe(true);
  }));

  it('should emit close event when close button is clicked', fakeAsync(() => {
    let closed = false;
    component.close.subscribe(() => {
      closed = true;
    });

    fixture.componentRef.setInput('closable', true);
    fixture.detectChanges();
    tick(20);

    const compiled = fixture.nativeElement as HTMLElement;
    const closeButton = compiled.querySelector('.toast_close') as HTMLButtonElement;
    closeButton?.click();
    fixture.detectChanges();

    tick(300);
    expect(closed).toBe(true);
  }));

  it('should hide toast when closed', fakeAsync(() => {
    fixture.componentRef.setInput('closable', true);
    fixture.detectChanges();
    tick(20);

    const compiled = fixture.nativeElement as HTMLElement;
    const closeButton = compiled.querySelector('.toast_close') as HTMLButtonElement;
    closeButton?.click();
    fixture.detectChanges();

    expect(component.isVisible()).toBe(false);
  }));
});
