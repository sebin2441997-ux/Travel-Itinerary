import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AppComponent } from './app.component';
import { TripFormComponent } from './components/trip-form/trip-form.component';
import { ChatInterfaceComponent } from './components/chat-interface/chat-interface.component';
import { ItineraryDisplayComponent } from './components/itinerary-display/itinerary-display.component';
import { RagItineraryComponent } from './components/rag-itinerary/rag-itinerary.component';
import { ApiService } from './services/api.service';

@NgModule({
  declarations: [
    AppComponent,
    TripFormComponent,
    ChatInterfaceComponent,
    ItineraryDisplayComponent,
    RagItineraryComponent
  ],
  imports: [
    BrowserModule,
    CommonModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule
  ],
  providers: [ApiService],
  bootstrap: [AppComponent]
})
export class AppModule { }
