import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component, TemplateRef, ViewChild, ViewContainerRef } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { Dropdown } from './dropdown';

@Component({
  template: `
    <div>
      <button #trigger [libDropdown]="dropdownTemplate" [dropdownData]="testData">
        Open Dropdown
      </button>
      <ng-template #dropdownTemplate let-data>
        <div class="dropdown-content">Dropdown Content: {{ data }}</div>
      </ng-template>
    </div>
  `,
  standalone: true,
  imports: [Dropdown],
})
class TestHostComponent {
  @ViewChild('dropdownTemplate') dropdownTemplate!: TemplateRef<any>;
  testData = 'test-value';
}

describe('Dropdown', () => {
  let component: Dropdown;
  let fixture: ComponentFixture<TestHostComponent>;
  let triggerElement: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Dropdown, TestHostComponent, BrowserAnimationsModule],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    fixture.detectChanges();

    const directiveElement = fixture.debugElement.query((el) => el.name === 'button');
    component = directiveElement.injector.get(Dropdown);
    triggerElement = directiveElement.nativeElement;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should open dropdown when trigger is clicked', () => {
    expect(component.isDropdownOpen()).toBe(false);

    triggerElement.click();
    fixture.detectChanges();

    expect(component.isDropdownOpen()).toBe(true);
  });

  it('should close dropdown when trigger is clicked again', () => {
    triggerElement.click();
    fixture.detectChanges();
    expect(component.isDropdownOpen()).toBe(true);

    triggerElement.click();
    fixture.detectChanges();
    expect(component.isDropdownOpen()).toBe(false);
  });

  it('should emit dropdownOpened when opened', () => {
    spyOn(component.dropdownOpened, 'emit');

    triggerElement.click();
    fixture.detectChanges();

    expect(component.dropdownOpened.emit).toHaveBeenCalled();
  });

  it('should emit dropdownClosed when closed', () => {
    spyOn(component.dropdownClosed, 'emit');

    triggerElement.click();
    fixture.detectChanges();
    triggerElement.click();
    fixture.detectChanges();

    expect(component.dropdownClosed.emit).toHaveBeenCalled();
  });

  it('should close dropdown when clicking outside', () => {
    triggerElement.click();
    fixture.detectChanges();
    expect(component.isDropdownOpen()).toBe(true);

    document.body.click();
    fixture.detectChanges();

    expect(component.isDropdownOpen()).toBe(false);
  });

  it('should pass dropdownData to template', () => {
    triggerElement.click();
    fixture.detectChanges();

    const overlayPane = document.querySelector('.cdk-overlay-pane');
    expect(overlayPane?.textContent).toContain('test-value');
  });
});
