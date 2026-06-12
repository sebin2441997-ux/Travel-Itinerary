import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { TripPreferences, TripItinerary, ChatMessage } from '../models/itinerary.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;
  private ragBaseUrl = environment.ragApiUrl || 'http://localhost:5001/api/rag';

  constructor(private http: HttpClient) { }

  healthCheck(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`);
  }

  generateItinerary(preferences: TripPreferences): Observable<any> {
    return this.http.post(`${ this.baseUrl }/generate`, preferences);
  }

  sendChatMessage(
    message: string,
    conversationHistory: ChatMessage[],
    tripContext?: TripPreferences
  ): Observable<any> {
    return this.http.post(`${ this.baseUrl }/chat`, {
      message,
      conversation_history: conversationHistory,
      trip_context: tripContext
    });
  }

  searchPlaces(destination: string, category: string = 'tourist_attraction'): Observable<any> {
    const params = new HttpParams()
      .set('destination', destination)
      .set('category', category);

    return this.http.get(`${ this.baseUrl }/places/search`, { params });
  }

  exportItinerary(itinerary: TripItinerary, format: string = 'text'): Observable<any> {
    return this.http.post(`${ this.baseUrl }/export`, {
      itinerary,
      format
    });
  }

  // RAG-specific methods (use separate RAG backend on port 5001)
  uploadRAGDocument(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${ this.ragBaseUrl }/upload`, formData);
  }

  generateRAGItinerary(preferences: TripPreferences): Observable<any> {
    return this.http.post(`${ this.ragBaseUrl }/generate`, preferences);
  }

  searchRAGDocuments(query: string, k: number = 5): Observable<any> {
    return this.http.post(`${ this.ragBaseUrl }/search`, { query, k });
  }

  getRAGDocuments(): Observable<any> {
    return this.http.get(`${ this.ragBaseUrl }/documents`);
  }

  clearRAGDocuments(): Observable<any> {
    return this.http.delete(`${ this.ragBaseUrl }/documents/clear`);
  }
}