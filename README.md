# Assignment Submission Portal

This is a RESTful application that provides APIs for assignment submission. It allows users to upload assignments and admins to review them. The application uses MongoDB Atlas as its database and incorporates JWT and OAuth for authentication.

## Setup

1. Clone this repository:

```bash 
git clone https://github.com/harshithvh/assignment-portal.git
cd assignment-portal
```

2. Create a `.env` file:
```bash
MONGO_USERNAME=MONGODB_USERNAME
MONGO_PASSWORD=MONGODB_PASSWORD
SECRET_KEY=YOUR_SECRET_KEY
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

3. Build the Docker Image:
```bash 
docker-compose up --build
```

- This command will:
  - Build the application image using the `Dockerfile`.
  - Set up MongoDB as a service, as defined in the `docker-compose.yml` file.

4. Access the Swagger UI:
```bash 
http://localhost:8000/docs
```

5. Stopping the Containers:
```bash 
docker-compose down
```

## Debugging

- If stuck, check the `server.log` file for error messages or warnings.
- Ensure your IP address is whitelisted in MongoDB Atlas.
- Verify Database User Permissions.
- Double-check `.env` file, all placeholders must be replaced with actual credentials.
- Verify your cluster's status in the main dashboard - should show Deployed / Running.

## Further Improvements

- Implement rate limiting to prevent abuse of the API.
- Implement file storage for assignment uploads (e.g., AWS S3).
- Implement refresh tokens for prolonged sessions without requiring re-authentication.
- Implement file versioning to track changes in assignments over time.
- Add more detailed user profiles and assignment metadata.
- Implement caching mechanisms (e.g., Redis)
