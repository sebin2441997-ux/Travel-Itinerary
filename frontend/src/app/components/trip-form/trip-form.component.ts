import { Component, EventEmitter, Output } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { TripPreferences } from '../../models/itinerary.model';

@Component({
  selector: 'app-trip-form',
  templateUrl: './trip-form.component.html',
  styleUrls: ['./trip-form.component.scss']
})
export class TripFormComponent {
  @Output() formSubmit = new EventEmitter<TripPreferences>();
  
  tripForm: FormGroup;
  
  budgetOptions = ['budget', 'moderate', 'luxury'];
  paceOptions = ['relaxed', 'moderate', 'packed'];
  
  interestOptions = [
    'History & Culture',
    'Food & Dining',
    'Nature & Outdoors',
    'Art & Museums',
    'Shopping',
    'Nightlife',
    'Adventure Sports',
    'Photography',
    'Local Experiences',
    'Relaxation'
  ];

  constructor(private fb: FormBuilder) {
    this.tripForm = this.fb.group({
      destination: ['', Validators.required],
      start_date: ['', Validators.required],
      end_date: ['', Validators.required],
      budget: ['moderate'],
      interests: [[]],
      pace: ['moderate'],
      accommodation_location: [''],
      dietary_restrictions: [[]],
      transportation_preference: ['mixed']
    });
  }

  onSubmit() {
    if (this.tripForm.valid) {
      console.log("Inside Form submit", this.tripForm.value)
      this.formSubmit.emit(this.tripForm.value);
    }
  }

  toggleInterest(interest: string) {
    const interests = this.tripForm.get('interests')?.value || [];
    const index = interests.indexOf(interest);
    
    if (index > -1) {
      interests.splice(index, 1);
    } else {
      interests.push(interest);
    }
    
    this.tripForm.patchValue({ interests });
  }

  isInterestSelected(interest: string): boolean {
    const interests = this.tripForm.get('interests')?.value || [];
    return interests.includes(interest);
  }
}
