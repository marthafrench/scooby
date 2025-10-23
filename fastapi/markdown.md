marketsai/                              # Single monorepo
│
├── backend/                            # FastAPI backend
│   ├── __init__.py
│   ├── main.py                         # FastAPI app entry point
│   │
│   ├── controllers/                    # API Controllers (like @RestController)
│   │   ├── __init__.py
│   │   ├── resolution_controller.py   # Resolution API endpoints
│   │   ├── codebard_controller.py     # CodeBard API endpoints
│   │   ├── health_controller.py       # Health check endpoints
│   │   └── gcs_controller.py          # GCS endpoints
│   │
│   ├── services/                       # Business Logic (like @Service)
│   │   ├── __init__.py
│   │   ├── resolution_service.py      # Resolution business logic
│   │   ├── codebard_service.py        # CodeBard business logic
│   │   ├── llm_service.py             # Shared LLM wrapper
│   │   ├── document_service.py        # Document retrieval
│   │   ├── prompt_service.py          # Prompt management
│   │   └── gcs_service.py             # GCS operations
│   │
│   ├── repositories/                   # Data Access (like @Repository)
│   │   ├── __init__.py
│   │   ├── document_repository.py     # Document storage/retrieval
│   │   └── prompt_repository.py       # Prompt storage
│   │
│   ├── models/                         # Domain Models
│   │   ├── __init__.py
│   │   ├── schemas.py                 # Pydantic models
│   │   └── domain.py                  # Business domain models
│   │
│   ├── config/                         # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py                # App settings
│   │   └── dependencies.py            # Dependency injection
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py
│   │
│   └── tests/
│       ├── test_controllers.py
│       ├── test_services.py
│       └── test_repositories.py
│
├── frontend/                           # Django UI
│   ├── marketsai/                      # Django project
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── apps/
│   │   ├── resolution/                 # Resolution UI
│   │   │   ├── views.py               # Like @Controller
│   │   │   ├── urls.py
│   │   │   └── templates/
│   │   │
│   │   ├── codebard/                   # CodeBard UI
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── templates/
│   │   │
│   │   └── dashboard/
│   │       ├── views.py
│   │       ├── urls.py
│   │       └── templates/
│   │
│   └── static/
│
├── shared/                             # Shared utilities
│   ├── __init__.py
│   ├── constants.py
│   └── utils.py
│
├── docker-compose.yml
├── requirements.txt
└── README.md
