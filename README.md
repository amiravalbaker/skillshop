# skillshop

Website project by Amira Val Baker

## Application Purpose

Skillshop is a service provider application. It allows users as skilled service providers to create listings offering their skill as a service. It allows users looking for the services of a skilled provider to search for a specific skill within a specified radius from their location. 


## Repository

The Github repo can be found here.

https://github.com/amiravalbaker/skillshop


## Agile Planning

This project followed an agile methodology utilising a project board, user stories and wireframes.

The project Board, with user stories can be found here.

https://github.com/amiravalbaker


# **THE BUILD** #

**Design Layout**

The application provides a simple design centred around the application logo set on a white background.


#### Wireframe

The wireframes were drawn by hand.

**Logo**

The logo was made using photoshop and stylised with AI.
The image on lthe eft is the original and the image on the rigght is after AI made it look "stylish and professional.

**Colour Palette**

A colour palette was found from the image using the website https://imagecolorpicker.com/. The colour theme was 

![alt text](.jpg) add an images of the website on a desktop, tablet and phone


### Database

Skillshop uses PostgreSQL as its primary database. 

The database was created with the use of Python classes, known as models in the Django framework. These models define the structure of your database table.
The models used in skillshop were defined using an Entity Relationship diagram. 

INPUT ERD HERE



![Skill Model](readme/task-model.png)

1. **User Model**:
   - This is the built-in Django `User` model which includes fields like `id`, `username`, `email`, and `password`. 

2. **Profile Model**:
   - `Profile` has a one-to-one relationship with the `User` model.
   - Fields:
     - `user`: A one-to-one field linking to the `User` model.
     - `profile_picture`: A Cloudinary field for storing profile pictures.

3. **Skill Model**:
   - `Task` has a many-to-one relationship with the `User` model.
   - Fields:
     - `title`: A character field for the task title.
     - `description`: A text field for the task description.
     - `status`: A character field with choices for task status.
     - `created`: A datetime field for when the task was created.
     - `due_date`: A datetime field for the task's due date.
     - `completed_date`: A datetime field for when the task was completed.
     - `priority`: A character field with choices for task priority.
     - `category`: A character field with choices for task category.
     - `user`: A foreign key linking to the `User` model.



Relationships

- **User to Profile**: One-to-One relationship.
- **User to Task**: One-to-Many relationship.

## AI Usage

AI was used for:
advice with structuring the models

generating code from logic instructions especially the views and templates.
Debugging and fixing errors in the code and deployment issues

## Deployment

Deploying the application to heroku was done as follows:

   - Project uploaded to a github repository
   - Gunicorn installed and configured
   - All dependencies are listed in `requirements.txt` and the p
ython version is listed in `.python-version`
   - configure static files and settings.py, paying special attention to disabling debugging and any other settings related to security.
   - set up and configure environmental files eg. `env.py`
   - create a `Procfile`. This file tells Heroku how to run your application.
   - ensure that any files that contain secret keys or other sensitive information eg. `env.py` is added to `.gitignore` and is not present in your github repo
  
2. **Deploying to Heroku**
   - Create heroku app
   - Link github repository & Code Institute PostGres database
   - Add environmental variables to heroku, such as, secret keys.
   - Deploy the application

## Testing

USER STORY	ACTION	EXPECTED RESULT	TEST	
*User SignUp**	| Navigate to signup page. Enter valid details and submit. 	|User is registered and re-directed to the home page with a confirmation message that they have signed up and a link to their profile in the nav bar.	|PASS	|
				
	| Attempt to register with an existing username or email.	| Gives warning message "A user with that username already exists." 	|PASS	|
**User Login**	| Navigate to the login page. Fill in the form with valid credentials and submit.	| User is logged in and redirected to the home page with a confirmation message that they have logged in and a link to their profile in the nav bar.	|PASS	|
	| Attempt to log in with invalid credentials.	| Gives warning message "The username and/or password you specified are not correct."	|PASS	|
**User Logout**	| While logged in, click the logout button.	| User is asked for confirmation and upon confirming they are logged out and redirected to the home page.	|PASS	
**View Profile**	| Navigate to the profile page.	| User clicks link in the navbar and is redirected to profile page.	|PASS	
				
**Edit Profile**	| Navigate to edit profile page 	| User selects edit profile button and is re-directed to the edit profile page.	|PASS	|
	| Make edits to your profile	User updates their details and submits. They are re-directed to their profile page with a confirmation message	|PASS	|
**Update Profile Image**	| On the profile page, upload a new profile picture.	| Profile picture is updated and displayed correctly.	|PASS	|
**Delete Profile**	| Delete profile from edit profile page	|User selects delete their profile account with a warning message asking if they are sure. If they confirm they are redirected back to the home page with a confirmation message.	|PASS	|
**Create Listing**	| Create a new listing from 	|A user that has selected the provider option in their profile page can navigate to the create a listing page from the nav bar, the home page and their profile page. 	|PASS	|
**Edit Listing**	| Edit a listing from listing page	| User selects edit listing, is taken to the edit listing page, makes edits, submits and is redirected to listing page with a confirmation message.	|PASS	|
**Delete Listing**	| Delete listing from edit listing page	| User selects delete their profile account with a warning message asking if they are sure. If they confirm they are redirected back to the home page with a confirmation message.	|PASS	|
**Search listings by skill**	| Search for a skilled provider from the search page	| user selects a skill from the drop down menu, selects search and the search results are shown below. 	|PASS	|
**Search listings by location**	| Search for a skilled provider from the search page by location	| user selects location by either detecting location or manually typing the location, clicks search and the search results are shown below in order of distance.	|PASS	|
	| Search for a skilled provider from the search page within a certain radius	| user selects desired radius, clicks search and the search results are shown below in order of distance.	|PASS	|
**contact listing pr ovider**	| Contact the skilled provider from their listing page	| User selects  message provider, is redirected to a messaging page, write message, submits and is shown message in converstaion detail.	|PASS	|
**Leave review**	| Leave a review while on listing page	|A user that has had a conversation with the listing provider can leave a review, submit and the review appears immediately.	|PASS	|
**Edit Review**	| Edit  your review from listing page	| A user selects edit review, edits the review, selects update review and the updated review appears immediately.	|PASS	|
**Delete Review**	| Delete review from listing page	| User selects delete review with a warning message asking if they are sure. If they confirm they are rredirected to the listing page with a confirmation message.	|PASS	|
                                                                                            |

## Responsivity



## Future Developments


### Email Notifications

One of the key features planned for future development is the integration of email notifications. Users will be able to receive email reminders for upcoming due dates, task deadlines, and important updates. Additionally, users could also have the option to customize the frequency and type of notifications they wish to receive.

### Account Reset Using Email

Another important feature is the ability to reset account passwords using email. The process will involve sending a password reset link to the user's registered email address, allowing them to set a new password. This feature will enhance the security and user-friendliness of the application, ensuring that users can easily regain access to their accounts.

## Validation

### Lighthouse
### Accessibility


### HTML

There were no HTML errors but the lighthouse report did show some room for improvement.

### CSS



### Jquery


### Python


