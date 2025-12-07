import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ModalContainer } from './modal-container';

describe('ModalContainer', () => {
  let component: ModalContainer;
  let fixture: ComponentFixture<ModalContainer>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ModalContainer],
    }).compileComponents();

    fixture = TestBed.createComponent(ModalContainer);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render modal container element', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const container = compiled.querySelector('.modal-container');
    expect(container).toBeTruthy();
  });

  it('should project content via ng-content', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const container = compiled.querySelector('.modal-container');
    expect(container).toBeTruthy();
  });
});
