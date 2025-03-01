## What is Nursing Assistant Application?
### Purpose
#### Assist nurses by automating administrative tasks, providing clinical decision support, and enhancing patient care through AI-driven workflows.
### Key Functions
##### - Automate patient handoffs.
##### - Generate shift summaries.
##### - Generate draft responses for patient messages
### Technologies
##### - Frontend: React/Flask for user interface.
##### - Backend: Python (FastAPI) -- The motivation is to provide middleware and dependency injection similar to Spring DI, which is reliable for easy backend API implementation and modularization.
##### - ORM: SQLModel -- The motivation is to provide database relation mapping to PostgreSQL, similar to Java Hibernate, using an object-oriented approach for database query integration.
##### - Data Validation: Pydantic -- The motivation is to provide a separation of concerns similar to the MVC framework (Java Struts 2), where the Controller and View are responsible for form validation and entity management.
##### - Application Monitoring Tool : Logfire -- The motivation is to facilitate the easy integration with Operations similar to APM (Appdynamics), particularly for investigation and efficient bug fixing.
##### - Structured Logging : Loguru -- The motivation is to facilitate the easy integration with Operations particularly with ELK.
##### - Database: PostgreSQL
##### - AI: Generative AI models ChatGPT for report generation
##### - Security: OAuth2 for authentication
🟢 **Note:** 🟢 Technical Disclaimer: The API key implementation and format are derived from the official documentation. Please refer to the documentation for accuracy and updates. https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

## What is the process flow of Patient Handoffs?
### Step 1: Trigger Handoff Process:
##### - Nurse initiated handoff at shift change or patient transfer.
##### - System identifies patients assigned to the nurse (query Patients table by nurse_id).
### Step 2: Data Collection:
##### - Query VitalSigns, MedicalData, and NurseNotes tables for latest patient data:
##### - Vital signs: Latest timestamp from VitalSigns (e.g., BP, HR, O2 sat).
##### - Medical data: Recent entries from MedicalData (e.g., medications, lab results).
##### - Nurse notes: Relevant updates from NurseNotes (e.g., condition changes).
### Step 3: AI-Generated Draft Report:
##### - AI (e.g., ChatGPT) generates draft handoff report using SBAR format:
##### - Situation: Current patient status (e.g., "Stable, BP 130/80").
##### - Background: Diagnosis, admission date (from Patients table).
##### - Assessment: Recent changes (from VitalSigns, MedicalData, NurseNotes).
##### - Recommendation: Alerts and tasks (e.g., "Monitor respiratory status").
##### - Store draft in Handoffs table (status = "draft").
---
## How API keys generation works?
### Endpoint: /token
##### - A requests for an API key through endpoint /token
##### - Verifies if the user has the right permission to generate API key
##### - If all the checks are verified, a unique API key is generated using OAuth2 with Password (and hashing), Bearer with JWT tokens
##### - The key is stored in api_keys table along with metadata
##### - The API key is displayed to the user only once
![image](https://github.com/user-attachments/assets/2594dc35-5323-4c89-a0a2-662842ab1d78)
---
## How does using an API in a request work?
### Endpoint: Any protected endpoint
##### - The user includes the API key in their request, HTTP headers:
#####     GET /api/resource
#####     Authorization: Bearer <API_KEY>
##### - When a request is received, the following are checks:
######     - If the API key exists in the database
######     - If it is active (is_active = true)
######     - If it has expired (expires_at > current)
######     - If the user associated is still active

##### - Process the request or reject it
##### - If the key is valid, the request proceeds
##### - If the key is invalid, the endpoint returns 401 Unauthorized : The API key validation was unsuccessful.
![image](https://github.com/user-attachments/assets/7ca2c75f-603c-40fe-9d10-b55f579057ee)

## Resources:
##### https://lucid.app/lucidchart/17225731-5e2d-43ba-8e75-d1d50cf66608/edit?viewport_loc=-418%2C-449%2C3783%2C1471%2C0_0&invitationId=inv_ccd80c58-1618-464d-a2db-537b8b0d57b1
