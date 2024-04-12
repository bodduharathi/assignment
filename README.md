bodduharathi8@gmail.com
Harathi Boddu
LOOP ASSIGNMENT
### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
   ```

2. **Install Dependencies**

   Install Django and other required packages using pip.

   ```bash
   pip install django pytz
   ```

### Database Setup 

```bash
python manage.py migrate
```

### Load Initial Data 

```bash
python load_data.py
```

### Running the Server

Start the Django development server.

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`.

## Testing API Endpoints

Use tools like Postman or curl to test the API endpoints.

1. **Trigger Report Generation**

   Send a POST request to trigger report generation:

   ```bash
   http://127.0.0.1:8000/api/trigger_report/
   ```

2. **Get Report Status**

   Send a GET request to check the status of a report:

   ```bash
   http://127.0.0.1:8000/api/get_report/?report_id=<report_id>
   ```

   Replace `<report_id>` with the actual report ID.

