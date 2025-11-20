# What was new in this version-2 ?
1. Now the users In the registration form can directly upload their fingerprint. via file or physical scanned his fingerprint by using their fingerprint devices. And also capture the live image. or upload the image by his choice.
2. In the view portal. the QR is now equipped with Aadhaar ID number and Unique section id.
3. Also, we enhance the user experience with smooth api calls. and also running the application in the low Internet connectivity without any failures. and monitoring the application health on the Voter Officer dashboard.
4. We deeply focused on low Internet connectivity issue in remote areas .And we have introduced some solutions to solve the low Internet issue and system failure By using Google Technologies and Ai drives. That make the application to work even in low Internet connectivity or In case of system failures.

# Secure Aadhaar Voting


This project is a web-based portal for verifying voters using facial recognition. It provides a simple interface for an operator to look up a voter by their Aadhaar number and verify their identity by comparing a live photo with the one stored in the database. The application is built with a Python Flask backend, a simple HTML/CSS/JS frontend, and is designed for deployment on Google App Engine.


You can refer to the Code repository. At the end of this document..
## Tech Stack


- **Languages**: Python 3.11, HTML, CSS, JavaScript
- **Frameworks**: Flask (v3.1.0)
- **Libraries**:
  - Gunicorn (v23.0.0): WSGI HTTP Server for UNIX.
  - PyMySQL (v1.1.1): Python MySQL client library.
  - google-cloud-vision: Google Cloud Vision API client for face detection and comparison.
  - Jinja2 (v3.1.6): Templating engine for Python.
- **Infrastructure & Services**:
  - **Hosting**: Google App Engine (Flexible Environment)
  - **Database**: Google Cloud SQL for MySQL
  - **AI/ML Service**: Google Cloud Vision API

## Architecture


The system is composed of three main parts: a frontend web interface, a backend Flask application, and Google Cloud services for data storage and facial recognition.


```
+-------------------+      HTTPS      +---------------------------------+
|  User's Browser   | <------------>  |      Google App Engine          |
| (HTML/CSS/JS)     |                 |  (Flask App on Gunicorn)        |
+-------------------+                 +---------------------------------+
      ^      |                                   |            ^
      |      | User captures live image,         |            |
      |      | enters Aadhaar number             |            |
      |      v                                   | (API Call) | (SQL Connection)
+-------------------+      (Verification)     +--------------------+   +---------------------+
| Facial Recognition| <-------------------- | /validate-face API |-->| Google Cloud SQL    |
| (Google Vision API)|                       +--------------------+   | (MySQL Database)    |
+-------------------+                                                +---------------------+
```


**Data Flow:**


1.  The user accesses the portal, which is served by the Flask application running on Google App Engine.
2.  On the "Facial Recognition System" page (`faportal.html`), the user enters an Aadhaar number and allows the browser to access their camera.
3.  The user captures a live image, which is converted to a Base64 string on the client-side.
4.  The form, containing the Aadhaar number and the image data, is submitted to the `/validate-face` endpoint on the Flask backend.
5.  The backend queries the Google Cloud SQL database to retrieve the stored reference photo for the given Aadhaar number.
6.  The backend sends both the live-captured image and the stored reference image to the Google Cloud Vision API for comparison.
7.  The Vision API returns a similarity score.
8.  The Flask application processes this score, determines if the verification is successful, and returns a JSON response to the frontend.
9.  The frontend JavaScript dynamically updates the page to show a success or failure message.


## Core Features


-   **Real-time Face Verification**: Securely verifies a voter's identity by comparing a live image with a database record, reducing the risk of impersonation.
-   **Aadhaar-Based Search**: Provides a simple and unique way to look up voter records using their Aadhaar number.
-   **Web-Based Interface**: Offers an accessible portal that can be used on any device with a web browser and a camera, without needing special software.


## Setup & Run Guide


### Prerequisites


-   Python 3.11
-   A Google Cloud Project with:
    -   Google App Engine enabled.
    -   Google Cloud SQL Admin API enabled.
    -   Google Cloud Vision API enabled.
-   A Google Cloud SQL for MySQL instance.
-   Google Cloud SDK installed and authenticated (`gcloud auth login`).


### Local Setup


1.  **Clone the repository:**
    ```bash
    git clone <https://github.com/vikasgurram26/Voter-Application-Version-2.git>
    cd <voter-application-v2>
    ```


2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # On Windows: .\.venv\Scripts\activate
    ```


3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```


4.  **Configure Environment Variables:**
    -   Create a `.env` file by copying the example: `cp .env.example .env`
    -   Fill in the values in the `.env` file with your database credentials and GCP details.
    -   Download your Google Cloud service account JSON key and set the `GOOGLE_APPLICATION_CREDENTIALS` variable to its path.


5.  **Database Setup:**
    -   Connect to your Cloud SQL instance.
    -   Create a database (e.g., `Voter-Database`).
    -   Create the required tables. Example schema:
        ```sql
        CREATE TABLE voters (
            aadhaar_number VARCHAR(255) NOT NULL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            photo_url VARCHAR(255) NOT NULL 
        );
        ```


6.  **Run the application locally:**
    ```bash
    flask run
    ```
    The app will be available at `http://127.0.0.1:5000`.


### Deployment


This project is configured for deployment to Google App Engine.


1.  Make sure your `app.yaml` is correctly configured with your environment variables and Cloud SQL instance connection name.
2.  Deploy the application using the Google Cloud SDK:
    ```bash
    gcloud app deploy
    ```


## Key APIs & Endpoints


### `POST /validate-face`


-   **Description**: Validates a voter's face against the stored record.
-   **Request Body**: `multipart/form-data`
    -   `aadhaar`: The voter's Aadhaar number.
    -   `live_image`: A Base64-encoded data URL of the image captured from the camera.
-   **Response**:
    -   **On Success (200 OK)**:
        ```json
        {
          "success": true,
          "message": "Face verification successful."
        }
        ```
    -   **On Failure (200 OK)**:
        ```json
        {
          "success": false,
          "message": "Face verification failed. Please try again."
        }
        ```


## What's Next


### Known Limitations


-   **Security**: Secrets like database passwords should be managed through Google Secret Manager instead of being in `app.yaml`.
-   **Frontend Feedback**: User feedback is currently handled by simple text and browser alerts, which could be improved with a better UI/UX.
-   **Scalability**: The current `F2` instance class in `app.yaml` is for basic workloads and may need to be adjusted for higher traffic.


### Future Improvements


-   **Integrate Google Secret Manager**: Store all secrets and credentials securely.
-   **Improve UI/UX**: Add more interactive animations and clearer, non-blocking notifications.
-   **Add Logging and Monitoring**: Integrate with Google Cloud's operations suite for better observability.
-   **Develop a Test Suite**: Implement unit and integration tests for the backend logic.


Updated GitHub Public Repository: https://github.com/vikasgurram26/Voter-Application-Version-2.git


 Demo Video Link :
 https://youtu.be/UjoFhH5CWKE 



