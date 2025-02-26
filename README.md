## What is Nursing Assistant Application?
### Purpose
#### Assist nurses by automating administrative tasks, providing clinical decision support, and enhancing patient care through AI-driven workflows.
### Key Functions
##### - Automate patient handoffs.
##### - Generate shift summaries.
##### - Generate draft responses for patient messages
### Technologies
##### - Frontend: React/Flask for user interface.
##### - Backend: Python (FastAPI)
##### - Database: PostgreSQL
##### - AI: Generative AI models ChatGPT for report generation
##### - Security: OAuth2 for authentication
---
## How API keys generation works?
### Endpoint: /token
##### - A requests for an API key through endpoint /token
##### - Verifies if the user has the right permission to generate API key
##### - If all the checks are verified, a unique API key is generated using OAuth2 with Password (and hashing), Bearer with JWT tokens
##### - The key is stored in api_keys table along with metadata
##### - The API key is displayed to the user only once
![image](https://github.com/user-attachments/assets/2594dc35-5323-4c89-a0a2-662842ab1d78)

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
