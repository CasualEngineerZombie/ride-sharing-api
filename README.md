## Django RESTful API for Ride Management

### Overview

This project implements a RESTful API using Django REST Framework to manage rides, users, and ride events. Key features include:

- **CRUD operations** on rides (with nested ride events and user details)
- **Authentication** ensuring that only users with the role `'admin'` can access the API
- **Pagination, filtering, and sorting** (by pickup time and distance from a provided GPS coordinate)
- **Performance optimizations** via `select_related` and `prefetch_related` (with custom queryset prefetching for ride events in the last 24 hours)

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/CasualEngineerZombie/ride-sharing-api.git
   ```
2. Navigate to the project directory:
   ```bash
   cd ride-sharing-api
   ```
3. Create and activate a virtual environment
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```
4. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Apply the migrations:

   ```bash
   python manage.py migrate

   ```

6. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:

   ```bash
   python manage.py runserver
   ```

### Raw SQL Report

The following raw SQL query returns the count of trips that took more than 1 hour from pickup to dropoff, grouped by month and driver. (It assumes that when a driver picks up a rider, a RideEvent with description 'Status changed to pickup' is created, and similarly for dropoff.)

```sql

SELECT DATE_TRUNC('month', pickup_event.created_at) AS month,
       CONCAT(driver.first_name, ' ', LEFT(driver.last_name, 1)) AS driver,
       COUNT(*) AS trip_count
FROM ride_app_ride AS ride
JOIN ride_app_rideevent AS pickup_event
  ON pickup_event.id_ride = ride.id_ride
  AND pickup_event.description = 'Status changed to pickup'
JOIN ride_app_rideevent AS dropoff_event
  ON dropoff_event.id_ride = ride.id_ride
  AND dropoff_event.description = 'Status changed to dropoff'
JOIN ride_app_user AS driver
  ON ride.id_driver = driver.id_user
WHERE dropoff_event.created_at - pickup_event.created_at > INTERVAL '1 hour'
GROUP BY month, driver
ORDER BY month, driver;

```

<i>Note: Adjust table names or SQL functions as needed based on your database system.</i>

### Additional Notes

<ul>
    <li>Authentication: Only users with the role 'admin' are permitted to use the API.</li>
    <li>Filtering & Sorting: Filtering by ride status and rider email is supported, along with ordering by pickup_time and by distance (when provided with lat and lng query parameters).</li>
    <li>Performance: The Ride List API minimizes the number of SQL queries (2 queries for rides with related users and recent ride events, plus 1 query for pagination count) as verified by Django Debug Toolbar. (Include screenshots in your repository as required.)</li>

</ul>
