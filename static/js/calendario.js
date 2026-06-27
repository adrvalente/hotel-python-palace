document.addEventListener("DOMContentLoaded", function() {
    const calendarEl = document.getElementById("calendar");

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        locale: "pt",
        height: "auto",
        events: "/api/reservas",

        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,listWeek"
        },

        buttonText: {
            today: "Hoje",
            month: "Mês",
            week: "Semana",
            list: "Lista"
        }
    });

    calendar.render();
});