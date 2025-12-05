import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FeaturesSection } from './features-section';
import { Icon } from 'shared-ui';

describe('FeaturesSection', () => {
  let component: FeaturesSection;
  let fixture: ComponentFixture<FeaturesSection>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FeaturesSection, Icon],
    }).compileComponents();

    fixture = TestBed.createComponent(FeaturesSection);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display heading', () => {
    const heading = fixture.nativeElement.querySelector('.features-section_heading');
    expect(heading).toBeTruthy();
    expect(heading.textContent).toContain('Why Choose Pages?');
  });

  it('should display subheading', () => {
    const subheading = fixture.nativeElement.querySelector('.features-section_subheading');
    expect(subheading).toBeTruthy();
  });

  it('should display all features', () => {
    const cards = fixture.nativeElement.querySelectorAll('.features-section_card');
    expect(cards.length).toBe(4);
  });

  it('should display feature titles', () => {
    const titles = fixture.nativeElement.querySelectorAll('.features-section_card-title');
    expect(titles.length).toBe(4);
    expect(titles[0].textContent).toContain('Lightning Fast');
    expect(titles[1].textContent).toContain('Team Collaboration');
    expect(titles[2].textContent).toContain('Secure & Private');
    expect(titles[3].textContent).toContain('Flexible Workspace');
  });

  it('should have responsive grid layout', () => {
    const grid = fixture.nativeElement.querySelector('.features-section_grid');
    expect(grid).toHaveClass('grid');
    expect(grid).toHaveClass('grid-cols-1');
    expect(grid).toHaveClass('md:grid-cols-2');
    expect(grid).toHaveClass('lg:grid-cols-4');
  });

  it('should display feature icons', () => {
    const icons = fixture.nativeElement.querySelectorAll('lib-icon');
    expect(icons.length).toBe(4);
  });
});
