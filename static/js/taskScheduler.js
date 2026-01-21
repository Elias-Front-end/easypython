document.addEventListener('DOMContentLoaded', function() {
    // Only init if we are in the runner app context
    // This script will be loaded by index.html
});

// We attach the scheduler logic to the Alpine component or a global object
// Since Alpine is used, we can extend the Alpine component or provide a helper

class TaskScheduler {
    constructor(containerId, appInstance) {
        this.containerId = containerId;
        this.app = appInstance; // Reference to Alpine app data
        this.calendar = null;
        this.init();
    }

    init() {
        const calendarEl = document.getElementById(this.containerId);
        if (!calendarEl) return;

        this.calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            themeSystem: 'standard', // or bootstrap but we use tailwind
            editable: true,
            selectable: true,
            events: this.loadEvents.bind(this),
            eventClick: this.handleEventClick.bind(this),
            select: this.handleDateSelect.bind(this),
            eventDrop: this.handleEventDrop.bind(this),
            height: 'auto',
            locale: 'pt-br'
        });

        this.calendar.render();
    }

    async loadEvents(fetchInfo, successCallback, failureCallback) {
        // Here we map existing tasks to calendar events
        // Since our tasks are mostly "Recurring" (Cron) or "Manual", visualization is tricky.
        // We will visualize:
        // 1. Past Executions (Logs) as completed events
        // 2. Scheduled Cron Jobs (Projection? - Hard to do accurately for infinite series)
        // For now, let's show Logs as "Past Events" and maybe "Mock" future events for Cron?
        
        // Strategy: Fetch Logs and map them
        try {
            // Fetch logs (using the new logs endpoint or tasks)
            // We need a way to get ALL logs or logs within range. 
            // The current API might need adjustment to filter by date range.
            // For MVP, we load tasks and show them as "All Day" if they have a schedule?
            // Actually, let's show *Past Executions* from logs.
            
            // Note: The user wants to "Schedule" tasks.
            // If we drag, we should update the task?
            // Let's stick to: Show Logs (History) and allow "New Task" on date select.

            const response = await fetch('/api/logs/?limit=100', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
            });
            const data = await response.json();
            
            const events = data.results.map(log => ({
                id: `log-${log.id}`,
                title: log.task_title || `Task #${log.task}`,
                start: log.created_at,
                backgroundColor: log.status === 'success' ? '#10B981' : (log.status === 'error' ? '#EF4444' : '#3B82F6'),
                borderColor: 'transparent',
                extendedProps: { type: 'log', ...log }
            }));

            successCallback(events);
        } catch (e) {
            console.error("Failed to fetch events", e);
            failureCallback(e);
        }
    }

    handleEventClick(info) {
        const props = info.event.extendedProps;
        if (props.type === 'log') {
            alert(`Execução: ${info.event.title}\nStatus: ${props.status}\nOutput: ${props.output?.substring(0, 100)}...`);
        }
    }

    handleDateSelect(info) {
        // Open Create Task Modal with pre-filled date? 
        // Our current Create Task is Cron based.
        // Maybe we just switch view to 'create' and let user know.
        if (confirm(`Criar nova tarefa para ${info.startStr}?`)) {
            // Access Alpine scope to switch view
            // This is a bit hacky, better to use Custom Events
            window.dispatchEvent(new CustomEvent('open-create-task', { detail: { date: info.startStr } }));
        }
    }

    handleEventDrop(info) {
        // Dragging logs doesn't make sense (history).
        // If we had future scheduled items, we would update them.
        if (info.event.extendedProps.type === 'log') {
            info.revert();
            alert('Não é possível mover registros históricos.');
        }
    }
}

// Expose to window
window.TaskScheduler = TaskScheduler;
