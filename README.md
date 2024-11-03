# Google Calendar API Python Project

This project allows you to interact with the Google Calendar API using Python. You can create, read, update, and delete calendar events, as well as schedule mindfulness and motivational reminders. This is perfect for automating task scheduling, reminders, and much more.

## Features

- **Create Events**: Schedule events such as workouts, meditation sessions, meetings, and more.
- **Read Events**: Retrieve and list upcoming events from your Google Calendar.
- **Update Events**: Modify existing events programmatically.
- **Delete Events**: Remove events from your calendar.
- **Automate Reminders**: Set reminders for events with customizable notification options.
- **Mindfulness Scheduling**: Schedule mindfulness events with a daily quote.
- **Motivational Scheduling**: Schedule motivational events with a daily quote.
- **Anime Episode Alerts**: Add events for upcoming anime episodes with notifications.
- **Manga Chapter Events**: Schedule events for new manga chapters with notifications.
- **Movie Recommendations**: Schedule movie sessions based on genre, rating, and period.

## Prerequisites

Before you can use the Google Calendar API, you must have a Google Cloud account and enable the Google Calendar API. Follow these steps:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the **Google Calendar API** in your project.
4. Create **OAuth 2.0 credentials** (OAuth client ID).
5. Download the `credentials.json` file from the Google Cloud Console and save it in the project directory.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/google-calendar-api-python.git
   cd google-calendar-api-python
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables in a `.env` file:

   ```plaintext
   API_NINJAS_KEY=your_api_ninjas_key
   VONAGE_API_KEY=your_vonage_api_key
   VONAGE_API_SECRET=your_vonage_api_secret
   USER_PHONE_NUMBER=your_phone_number
   ```

4. Run the application:

   ```bash
   uvicorn main:app --host 127.0.0.1 --port 7000 --reload
   ```

## Usage

- Access the API endpoints to create, read, update, and delete events.
- Schedule mindfulness and motivational events to receive daily quotes.
- Add alerts for anime episodes and manga chapters.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
