# tcp_course_project
This project was done by me as a assignment for university coursework.
___
**Theme**: Information system "Cinema" (ticket booking)\
**Main business process**: The client places an order for booking
a certain number of tickets to selected places. 
The administrator confirms the reservation after 
which the client in his profile can see a unique code 
by which he can buy tickets at the box office or 
online in his profile, no later than the time before 
the session.

**Functions of all users:**
* See movie sessions
* View free seats

**Functions of client:**
* Booking tickets
* Pay for tickets
* Cancel booking

**Functions of administrator (moderator):**
* View bookings
* Change status of bookings
* Add movie sessions

## Technologies Used:
* Python 3.10
* Django 4.0.1
* Bootstrap 5

## Usage:
1. Clone this repository
2. python manage.py makemigrations
3. python manage.py migrate
4. To use admin panel run python manage.py createsuperuser
5. python manage.py runserver

Then go to http://127.0.0.1:8000 in your browser

## Screenshots:
### Home
![Home page top](screenshots/home1.png)

![Home page bottom](screenshots/home2.png)

### Session detail
![Session page top](screenshots/session_page1.png)

![Session page top](screenshots/session_page2.png)

### Profile
![Profile](screenshots/profile1.png)

### Admin panel
![Admin panel](screenshots/admin1.png)

![Admin panel](screenshots/admin2.png)
