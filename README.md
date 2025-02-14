# Main Documentation TODO

## How API keys generation works?
### Endpoint: /token
##### - A requests for an API key through endpoint /token
##### - Verifies if the user has the right permission to generate API key
##### - If all the checks are verified, a unique API key is generated using OAuth2 with Password (and hashing), Bearer with JWT tokens
##### - The key is stored in api_keys table along with metadata
##### - The API key is displayed to the user only once
![image](https://github.com/user-attachments/assets/2594dc35-5323-4c89-a0a2-662842ab1d78)
