import logo from './logo.svg';
import './App.css';
import TripForm from './components/trip-form/TripForm';
import ItinerarySection from './components/itinerary/ItinerarySection';
import { useRef, useState } from 'react';

function App() {

  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);

  const itineraryRef = useRef(null);

  const handleGenerate = async (tripData) => {
    setLoading(true);
    console.log("HandleGenerate", tripData)
    setItinerary(tripData);
    itineraryRef.current?.scrollIntoView({
      behaviour: "smooth",
      block: "start"
    })


    //API call here

    setTimeout(() => {
      itineraryRef.current?.scrollIntoView({
        behaviour: "smooth",
        block: "start"
      })
      setLoading(false);

    }, 2000);
  };
  return (
    <div className="App">
      <TripForm onGenerate={handleGenerate} />
      <div id='itinerary-section' ref={itineraryRef}>
        <ItinerarySection itinerary={itinerary} loading={loading} />
      </div>
    </div>
  );
}

export default App;
