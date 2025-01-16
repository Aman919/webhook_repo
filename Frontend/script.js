let displayedEvents = [];

function fetchEvents() {
    fetch("http://localhost:5000/events")
        .then(response => response.json())
        .then(data => {

            if (data.events && data.events.length > 0) {
                const eventsContainer = document.getElementById("events-container");

                data.events.forEach(event => {
                    if (!displayedEvents.includes(event)) {
                        displayedEvents.unshift(event);

                        const eventElement = document.createElement('div');
                        eventElement.classList.add("event-item");
                        eventElement.textContent = event;

                        eventsContainer.insertAdjacentElement("afterbegin", eventElement);
                    }
                });
            }
        })
        .catch(error => {
            console.error("error fetching events: ", error);
        })
}

setInterval(fetchEvents, 15000);

fetchEvents();