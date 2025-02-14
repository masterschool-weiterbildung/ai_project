# Main Documentation TODO

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
![image](https://github.com/user-attachments/assets/c7a1e155-d420-4b82-93bf-59f8fcdf76f0)

