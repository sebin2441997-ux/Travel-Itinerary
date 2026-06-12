import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { TripPreferences, TripItinerary } from '../../models/itinerary.model';

@Component({
  selector: 'app-rag-itinerary',
  templateUrl: './rag-itinerary.component.html',
  styleUrls: ['./rag-itinerary.component.scss']
})
export class RagItineraryComponent implements OnInit {
  selectedFile: File | null = null;
  uploadedDocuments: string[] = [];
  totalChunks: number = 0;
  isUploading: boolean = false;
  isGenerating: boolean = false;
  uploadMessage: string = '';

  // Form data
  destination: string = '';
  startDate: string = '';
  endDate: string = '';
  budget: string = 'moderate';
  interests: string[] = [];

  // Results
  itinerary?: TripItinerary;
  searchResults: any[] = [];
  searchQuery: string = '';
  isSearching: boolean = false;

  // View state
  currentView: 'upload' | 'generate' | 'search' | 'results' = 'upload';

  availableInterests = [
    'Culture & History',
    'Food & Dining',
    'Nature & Outdoors',
    'Adventure',
    'Shopping',
    'Nightlife',
    'Relaxation'
  ];

  constructor(private apiService: ApiService) { }

  ngOnInit() {
    this.loadDocumentInfo();
  }

  loadDocumentInfo() {
    this.apiService.getRAGDocuments().subscribe({
      next: (response) => {
        if (response.success) {
          this.uploadedDocuments = response.documents.sources;
          this.totalChunks = response.documents.total_chunks;
        }
      },
      error: (error) => {
        console.error('Error loading documents:', error);
      }
    });
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      this.selectedFile = file;
      this.uploadMessage = `Selected: ${file.name}`;
    } else {
      this.uploadMessage = 'Please select a PDF file';
      this.selectedFile = null;
    }
  }

  uploadDocument() {
    if (!this.selectedFile) {
      this.uploadMessage = 'Please select a file first';
      return;
    }

    this.isUploading = true;
    this.uploadMessage = 'Uploading and indexing document...';

    this.apiService.uploadRAGDocument(this.selectedFile).subscribe({
      next: (response) => {
        this.isUploading = false;
        if (response.success) {
          this.uploadMessage = `✅ ${response.message} (${response.chunks_indexed} chunks indexed)`;
          this.selectedFile = null;
          this.loadDocumentInfo();
        } else {
          this.uploadMessage = `❌ Error: ${response.message}`;
        }
      },
      error: (error) => {
        this.isUploading = false;
        this.uploadMessage = `❌ Upload failed: ${error.message || 'Unknown error'}`;
      }
    });
  }

  toggleInterest(interest: string) {
    const index = this.interests.indexOf(interest);
    if (index > -1) {
      this.interests.splice(index, 1);
    } else {
      this.interests.push(interest);
    }
  }

  generateRAGItinerary() {
    if (!this.destination || !this.startDate || !this.endDate) {
      alert('Please fill in all required fields');
      return;
    }

    this.isGenerating = true;

    const preferences: TripPreferences = {
      destination: this.destination,
      start_date: this.startDate,
      end_date: this.endDate,
      budget: this.budget,
      interests: this.interests
    };

    this.apiService.generateRAGItinerary(preferences).subscribe({
      next: (response) => {
        this.isGenerating = false;
        if (response.success) {
          this.itinerary = response.itinerary;
          this.currentView = 'results';
        }
      },
      error: (error) => {
        this.isGenerating = false;
        alert('Error generating itinerary: ' + (error.message || 'Unknown error'));
      }
    });
  }

  searchDocuments() {
    if (!this.searchQuery.trim()) {
      return;
    }

    this.isSearching = true;

    this.apiService.searchRAGDocuments(this.searchQuery).subscribe({
      next: (response) => {
        this.isSearching = false;
        if (response.success) {
          this.searchResults = response.results;
        }
      },
      error: (error) => {
        this.isSearching = false;
        console.error('Search error:', error);
      }
    });
  }

  clearAllDocuments() {
    if (confirm('Are you sure you want to clear all uploaded documents? This cannot be undone.')) {
      this.apiService.clearRAGDocuments().subscribe({
        next: (response) => {
          if (response.success) {
            this.uploadMessage = '✅ All documents cleared';
            this.loadDocumentInfo();
          }
        },
        error: (error) => {
          alert('Error clearing documents: ' + error.message);
        }
      });
    }
  }

  switchView(view: 'upload' | 'generate' | 'search' | 'results') {
    this.currentView = view;
  }

  resetForm() {
    this.destination = '';
    this.startDate = '';
    this.endDate = '';
    this.budget = 'moderate';
    this.interests = [];
    this.itinerary = undefined;
    this.currentView = 'generate';
  }
}
