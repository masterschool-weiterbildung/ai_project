## AI Project Nursing Assistant Application
##### This repository contains the backend code for an AI-powered application developed as part of the Masterschool Weiterbildung AI Engineering program. The project provides API endpoints for various AI functionalities, including a chatbot feature leveraging agentic Retrieval-Augmented Generation (RAG). The codebase is structured to support a scalable and maintainable architecture.
---

## How to Install?
To set up the project locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone git@github.com:masterschool-weiterbildung/ai_project.git
   ```
2. **Navigate to the project directory:**:
   ```bash
   cd ai_project
   ```
3. **Create a virtual environment (recommended for dependency management):**:
   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment:**:
   - On Windows:
   ```bash
   venv\Scripts\activate
   ```
   - On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
5. **Backup Postgresql Database:**:
   1. Open pgAdmin, right-click the database, and select Backup.
   2. Create both a new database and a corresponding role/user on the target server.
   3. Restore the backup to the target database.
   4. Verify that tables, data, indexes, and constraints are present and correct.

---

## What is Nursing Assistant Application?
### Purpose
#### Assist nurses by automating administrative tasks, providing clinical decision support, and enhancing patient care through AI-driven workflows.
### Key Functions
##### - Automate patient handoffs.
##### - Chatbot for Patient
### Technologies
##### 🟢 Backend: Python (FastAPI) -- The motivation is to provide middleware and dependency injection similar to Spring DI, which is reliable for easy backend API implementation and modularization.
##### 🟢 ORM: SQLModel -- The motivation is to provide database relation mapping to PostgreSQL, similar to Java Hibernate, using an object-oriented approach for database query integration.
##### 🟢 Data Validation: Pydantic -- The motivation is to provide a separation of concerns similar to the MVC framework (Java Struts 2), where the Controller and View are responsible for form validation and entity management.
##### 🟢 Application Monitoring Tool : Logfire -- The motivation is to facilitate the easy integration with Operations similar to APM (Appdynamics), particularly for investigation and efficient bug fixing.
##### 🟢 Structured Logging : Loguru -- The motivation is to facilitate the easy integration with Operations particularly with ELK.
##### 🟢 Database: PostgreSQL
##### 🟢 AI: Generative AI models for report generation
##### 🟢 Security: OAuth2 for authentication

### Note: Technical Disclaimer: 
###### Certain implementations are derived from the official documentation. Please refer to the documentation.
###### https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
###### https://sqlmodel.tiangolo.com/tutorial/
###### https://docs.pydantic.dev/latest/api/base_model/
###### https://logfire.pydantic.dev/docs/integrations/web-frameworks/fastapi/

---

## How does the process flow for patient handoffs work?

<img width="915" alt="Screenshot 2025-04-21 at 20 04 51" src="https://github.com/user-attachments/assets/8d591ab4-e1b9-46e8-9014-89cd7757bf05" />

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

## Notable Implementations

#### Multi-model system
- gpt-4o-mini
- gemini-2.0-flash
- llama-3.3-70b-versatile
- grok-2-latest

#### Dynamic Prompting with PostgreSQL

#### Structured Output

## Technology Stack
- fastapi
- sqlmodel
- pydantic model


---

## How does Chatbot works?

<img width="981" alt="Screenshot 2025-06-04 at 11 13 00" src="https://github.com/user-attachments/assets/b86a8ad1-6aae-4459-99e2-6c7b675faf64" />

### Summary:
The chatbot functionality allows patients to send messages and ask questions about a particular medicine for an ailment or illness. This is a demonstration and prototype designed to showcase Retrieval-Augmented Generation (RAG), which is one of the most efficient and cost-effective ways for companies to build their own AI applications using Large Language Models (LLMs).
### Background and Motivation:
The traditional fine-tuning of LLM to improve performance has limitations.
- Temporal Limitations: Their training data is static, meaning they are unaware of events or developments occurring after their training cutoff (e.g., ChatGPT-4 has no knowledge of events post-April 2023).
- LLMs can generate confident but incorrect responses when dealing with unfamiliar topics.
- Public models do not have access to proprietary or private data.

## Notable Technologies/Implementations

#### Tool Calling

#### Agentic RAG

#### Persestence using Postgresql

## Technology Stack
- langchain
- langgraph
- pinecone
- langsmith
- postgresql

---

### What is Retrieval-Augmented Generation (RAG), and how does it address the limitations of traditional language models?

<img width="863" alt="Screenshot 2025-04-08 at 20 56 29" src="https://github.com/user-attachments/assets/c2a89bea-f7ff-44cc-a121-35bf541d69b8" />

RAG is presented as an effective solution to address the inherent limitations of LLMs. With RAG:

- Dynamic Knowledge Integration: The model retrieves specific information from a provided set of documents, ensuring accuracy.
- Reduced Hallucinations: By directly referencing supplied documents, the chance of generating incorrect information is minimized. 
- Real-Time Updates: The underlying data sources can be updated in real time.
- Transparency: Responses can include references to the source documents.

The document used in this RAG implementation can be found at: https://github.com/masterschool-weiterbildung/ai_project/tree/main/public/Who%20Essential%20Medicine.pdf

---

### How RAG Pipeline works?

<img width="978" alt="Screenshot 2025-04-08 at 21 04 33" src="https://github.com/user-attachments/assets/fcbbecfc-7de3-4992-a9d1-327e9aa88419" />

1. Documents are loaded using PyPDFLoader from a PDF file: https://github.com/masterschool-weiterbildung/ai_project/tree/main/public/Who%20Essential%20Medicine.pdf
2. Text is split into chunks that fit within the LLM’s context window.
3. Each chunk is embedded into a vector, meaning the text is converted into numerical representations using an embedding model.
   In this project, the pinecone/multilingual-e5-large embedding model is used.
   For efficiency, content-based IDs are implemented for each chunk.
5. Vectors are stored in a searchable vector index. This project uses Pinecone as the vector database.

When the application is active and a user submits an input prompt:

6. User input is embedded using the same embedding model.
7. Query vector is matched to document vectors to find the most relevant chunks ("top k").
8. Relevant chunks are added as context to the user’s query.
9. LLM generates a response based on both the query and context.

This RAG process helps the LLM give more accurate and grounded responses.

---

### How can we make our chatbot more conversational and implement Agentic RAG?

<img width="231" alt="Screenshot 2025-04-08 at 21 45 08" src="https://github.com/user-attachments/assets/2f059277-1b43-4722-a411-69388b76ae5e" />

1. To make our chatbot more conversational, we need to add memory to store the state of the conversation. We have two options: in-memory storage or using an external database. In our case, we utilized a Postgres checkpointer to provide context of previous interactions

---

### What is Tool Calling?

Tool calling allows AI models to interact directly with systems like databases or APIs, which require specific input formats. In our case, it’s a vector database.

<img width="900" alt="Screenshot 2025-04-08 at 21 55 31" src="https://github.com/user-attachments/assets/b0bf1929-4e1f-41af-bd2e-c9058fb729b7" />

2. Additionally, we need to incorporate the RAG approach mentioned above as a tool to create Agentic RAG. This enables the AI to take multiple steps in finding the best answer. Instead of performing just one search, it can decide what to look for, retrieve more information if needed, and even ask follow-up questions — all in order to provide smarter and more accurate responses.

---

### What tools and methods can we use to monitor and trace our chatbot application?

<img width="1388" alt="Screenshot 2025-04-09 at 19 39 51" src="https://github.com/user-attachments/assets/3f6908f6-12f6-40f9-a873-f16b90d1058a" />

- LangSmith is a platform to help developers build, debug, and monitor applications powered by large language models (LLMs). It provides tools for tracing, evaluating, and optimizing LLM workflows.

1. Query Received: The chatbot gets the question and starts processing it in the first "agent" step (0.82 seconds).
2. Decision to Retrieve: The "should_continue" step quickly decides that more information is needed, triggering the "tools" step
3. Data Retrieval: The "retrieve" step (11.04 seconds) searches for medicines related to African trypanosomiasis, taking the most time due to external data access.
4. Response Generation: A second "agent" step (3.47 seconds) processes the retrieved data with another model call, likely to organize the information into a coherent answer.
5. Completion: The final "should_continue" step confirms the process is done for this stage, and the trace ends successfully.


---

### How can we quantitatively measure the performance of agentic RAG?

**Langsmith Evals**

Evaluations provide a quantitative method for assessing the performance of LLM applications, which is crucial since LLMs can be unpredictable—minor alterations in prompts, models, or inputs may lead to substantial changes in outcomes.


<img width="853" alt="Screenshot 2025-04-11 at 10 19 32" src="https://github.com/user-attachments/assets/da9b815d-3da5-4f6c-b2c5-491faefff2c3" />

<img width="1396" alt="Screenshot 2025-04-12 at 09 37 09" src="https://github.com/user-attachments/assets/63105ae0-8132-44fd-bdf5-f7e2f2bc3b92" />


1. Correctness: Response vs reference answer
   - Goal: Measure "how similar/correct is the RAG chain answer, relative to a ground-truth answer"
   - Mode: Requires a ground truth (reference) answer supplied through a dataset
   - Evaluator: Use LLM-as-judge to assess answer correctness.
2. Relevance: Response vs input
   - Goal: Measure "how well does the generated response address the initial user input"
   - Mode: Does not require reference answer, because it will compare the answer to the input question
   - valuator: Use LLM-as-judge to assess answer relevance, helpfulness, etc.
3. Groundedness: Response vs retrieved docs
   - Goal: Measure "to what extent does the generated response agree with the retrieved context"
   - Mode: Does not require reference answer, because it will compare the answer to the retrieved context
   - Evaluator: Use LLM-as-judge to assess faithfulness, hallucinations, etc.
4. Retrieval relevance: Retrieved docs vs input
   - Goal: Measure "how relevant are my retrieved results for this query"
   - Mode: Does not require reference answer, because it will compare the question to the retrieved context
   - Evaluator: Use LLM-as-judge to assess relevance

**(Retrieval, Generation, Additional Requirement) framework using RAGAs**

<img width="774" alt="Screenshot 2025-05-18 at 23 54 44" src="https://github.com/user-attachments/assets/61dc45ac-3bbd-4334-a86b-467467deccf8" />

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
