import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Landing } from './landing';
import { RouterTestingModule } from '@angular/router/testing';

describe('Landing', () => {
  let component: Landing;
  let fixture: ComponentFixture<Landing>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Landing, RouterTestingModule],
    }).compileComponents();

    fixture = TestBed.createComponent(Landing);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render hero section', () => {
    const heroSection = fixture.nativeElement.querySelector('app-hero-section');
    expect(heroSection).toBeTruthy();
  });
});
