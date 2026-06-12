import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RagItineraryComponent } from './rag-itinerary.component';

describe('RagItineraryComponent', () => {
  let component: RagItineraryComponent;
  let fixture: ComponentFixture<RagItineraryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RagItineraryComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(RagItineraryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
