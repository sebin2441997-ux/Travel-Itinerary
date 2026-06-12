import React from "react";
import "./ItinerarySection.css";

function ItinerarySection({ itinerary, loading }) {
    console.log("Itinerary", itinerary)
    if (loading) {
        return (
            <section className="itinerary-section">
                <div className="itinerary-container">
                    <h2>Generating Your Travel Plan...</h2>

                    <div className="loading-spinner"></div>

                    <p>
                        Our AI is creating a personalized itinerary based on your
                        preferences.
                    </p>
                </div>
            </section>
        );
    }

    if (!itinerary) return null;

    return (
        <section className="itinerary-section">
            <div className="itinerary-container">
                <div className="itinerary-header">
                    <h2>Your Personalized Travel Itinerary</h2>

                    <div className="trip-summary">
                        <span>
                            📍 {itinerary.itinerary.destination}
                        </span>

                        <span>
                            🗓️ {itinerary.itinerary.duration}
                        </span>

                        <span>
                             {itinerary.itinerary.raw_itinerary} 
                        </span>
                    </div>
                </div>

                {/* <div className="days-container">
                    {itinerary.days.map((day) => (
                        <div className="day-card" key={day.dayNumber}>
                            <div className="day-header">
                                <h3>Day {day.dayNumber}</h3>
                                <span>{day.date}</span>
                            </div>

                            <div className="activities">
                                {day.activities.map((activity, index) => (
                                    <div
                                        className="activity-item"
                                        key={index}
                                    >
                                        <div className="activity-time">
                                            {activity.time}
                                        </div>

                                        <div className="activity-content">
                                            <h4>{activity.title}</h4>
                                            <p>{activity.description}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div> */}

                <div className="itinerary-actions">
                    <button className="action-btn">
                        Export PDF
                    </button>

                    <button className="action-btn">
                        Download Plan
                    </button>

                    <button className="action-btn secondary">
                        Regenerate
                    </button>
                </div>
            </div>
        </section>
    );
}

export default ItinerarySection;