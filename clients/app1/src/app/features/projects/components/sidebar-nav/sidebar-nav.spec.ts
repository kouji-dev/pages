import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SidebarNav, SidebarNavItem } from './sidebar-nav';
import { signal } from '@angular/core';

describe('SidebarNav', () => {
  let component: SidebarNav;
  let fixture: ComponentFixture<SidebarNav>;

  const mockItems: SidebarNavItem[] = [
    { label: 'Item 1', icon: 'file-text', active: true, onClick: vi.fn() },
    { label: 'Item 2', icon: 'users', active: false, onClick: vi.fn() },
  ];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SidebarNav],
    }).compileComponents();

    fixture = TestBed.createComponent(SidebarNav);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('items', mockItems);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display items', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const items = compiled.querySelectorAll('.sidebar-nav_nav-item');
    expect(items.length).toBe(2);
    expect(items[0].textContent).toContain('Item 1');
  });

  it('should handle click', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const items = compiled.querySelectorAll('lib-button');
    (items[1] as HTMLElement).click();
    expect(mockItems[1].onClick).toHaveBeenCalled();
  });
});
