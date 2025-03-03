# Django RESTful API for Ride Management

## Overview

This project implements a RESTful API using Django REST Framework to manage rides, users, and ride events. Key features include:

- **CRUD operations** on rides (with nested ride events and user details)
- **Authentication**: Only users with the role `admin` are permitted to access the API
- **Pagination, Filtering, and Sorting**:
  - Filter rides by status and rider email
  - Order rides by pickup time (ascending/descending) and by distance from a provided GPS coordinate
- **Performance Optimizations**:
  - **`select_related`**: Fetches related `id_rider` and `id_driver` objects in a single query.
  - **`prefetch_related`**: Custom prefetching retrieves only ride events from the last 24 hours, reducing unnecessary data load.
- **Minimal Database Queries**: The Ride List API retrieves data with only 2 queries (plus 1 for pagination count) as verified by Django Debug Toolbar.

## Setup Instructions

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

### Testing

A comprehensive suite of tests is included to ensure robust API behavior:

- Model Tests: Validate model methods, string representations, and relationships.
- Serializer Tests: Ensure that User, Ride, and RideEvent objects are correctly serialized and deserialized.
- Viewset Tests: Verify that API endpoints function as expected, including CRUD operations, filtering, ordering, and pagination.
- Permission Tests: Confirm that only users with the admin role can access the API endpoints.
  Filter Tests: Ensure that the filtering logic for rides (e.g., by status and rider email) works correctly.

<b>Running the Tests<b/>

```bash
   python manage.py test
```

### Performance Optimizations

<i>The API is optimized for performance using several advanced Django features:</i>

1. select_related: Used in the RideViewSet to fetch related id_rider and id_driver objects in one query.
2. prefetch_related: Custom prefetching is implemented to retrieve only the ride events from the last 24 hours, which significantly reduces the amount of data retrieved.
3. Query Counting: As verified by Django Debug Toolbar, the Ride List API performs only 2 main queries (plus 1 for pagination count) for retrieving rides and related data.
4. Efficient Distance Calculation: When sorting by distance, the API annotates the queryset with a computed distance using a single efficient SQL expression.

Screenshots of the Django Debug Toolbar demonstrating these optimizations are included in the repository.

> [!NOTE]
> Note: The extra queries you’re seeing in Django Debug Toolbar (for example, one query to retrieve the session and one for the authenticated user) aren’t part of the data retrieval logic for rides. They come from Django’s authentication and session middleware. These additional queries are expected when you’re using session authentication in a development environment.
