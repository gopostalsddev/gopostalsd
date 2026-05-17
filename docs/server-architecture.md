# Go Postal SD Server Architecture

## Overview

The Go Postal SD server is a Flask-based REST API that provides backend services for a postal and shipping management application. The architecture follows clean architecture principles with clear separation of concerns, dependency injection, and factory patterns.

## Architecture Principles

- **Clean Architecture**: Clear separation between controllers, services, repositories, and models
- **Dependency Injection**: Services are injected rather than directly instantiated
- **Factory Pattern**: Centralized object creation and configuration
- **Adapter Pattern**: Third-party integrations wrapped in adapters
- **Strategy Pattern**: Pluggable implementations for different services
- **Repository Pattern**: Data access abstraction

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  Frontend (React) │ Mobile App │ Third-party Integrations       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Layer (Routes)                         │
│  /api/auth │ /api/pricing │ /api/cart │ /api/print │ /api/contact │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Controller Layer                              │
│  AuthController │ PricingController │ CartController │ etc.     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Service Layer                                │
│  AuthService │ PricingService │ CartService │ EmailService      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Repository Layer                               │
│  UserRepository │ PricingRepository │ CartRepository │ etc.      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Data Layer                                   │
│  PostgreSQL Database │ Supabase Storage │ File System           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                Third-Party Integrations                          │
│  SinaliteAdapter │ MailerSendAdapter │ SMTPAdapter │ SupabaseAdapter │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Application Factory (`server/__init__.py`)

The main application factory creates and configures the Flask application:

```python
def create_server(config="development"):
    """Factory function to create and configure the Flask application."""
    server = Flask(__name__)
    
    # Load configuration
    server.config.from_object(DevelopmentConfig)
    
    # Initialize extensions
    database.init_app(server)
    migrate.init_app(server, database)
    sinalite.init_app(server)
    swagger.init_app(server)
    filestorage.init_app(server)
    
    # Initialize services using factory pattern
    main_factory = MainFactory()
    # ... service initialization
    
    # Register routes
    register_routes(server)
    
    return server
```

### 2. Factory Pattern (`server/factories/`)

The factory pattern provides centralized object creation:

#### MainFactory
- Coordinates all other factories
- Implements Singleton pattern
- Provides facade for service instantiation

#### ServiceFactory
- Creates service instances
- Handles service dependencies
- Manages service lifecycle

#### RepositoryFactory
- Creates repository instances
- Abstracts data access
- Provides repository dependencies

#### ControllerFactory
- Creates controller instances
- Handles controller dependencies
- Manages controller lifecycle

### 3. Service Layer (`server/services/`)

Business logic is encapsulated in services:

#### AuthService
- User authentication and authorization
- JWT token management
- Password hashing and validation
- Role-based access control

#### PricingService
- Product pricing calculations
- Integration with Sinalite API
- Pricing strategy implementation
- Store-specific pricing

#### CartService
- Shopping cart management
- Cart item operations
- Price calculations
- Shipping estimates

#### EmailService
- Email sending functionality
- Support for multiple providers (MailerSend, SMTP)
- Email templates and formatting
- Delivery tracking

### 4. Repository Layer (`server/repositories/`)

Data access is abstracted through repositories:

#### UserRepository
- User data operations
- Authentication data management
- Profile information handling

#### PricingRepository
- Product pricing data
- Store configuration
- Pricing history

#### CartRepository
- Cart persistence
- Cart item management
- Session handling

### 5. Controller Layer (`server/controllers/`)

Controllers handle HTTP requests and responses:

#### AuthController
- Login/logout endpoints
- User registration
- Password reset
- Email verification

#### PricingController
- Product pricing endpoints
- Store-specific pricing
- Bulk pricing operations

#### CartController
- Cart management endpoints
- Add/remove items
- Cart calculations

### 6. Model Layer (`server/models/`)

Data models represent the application's domain:

#### Authentication Models
- `User`: User account information
- `Role`: User roles and permissions
- `Permission`: Granular permissions
- `UserSession`: Active user sessions
- `PasswordResetToken`: Password reset tokens
- `EmailVerificationToken`: Email verification tokens

#### Product Models
- `PrintProduct`: Product information
- `PrintProductCategory`: Product categories
- `PrintProductType`: Product types
- `Vendor`: Product vendors

#### Pricing Models
- `ProductOption`: Product configuration options
- `ProductPricing`: Pricing information
- `ProductVariant`: Product variants
- `StoreCode`: Store-specific codes

#### Cart Models
- `Cart`: Shopping cart
- `CartItem`: Individual cart items
- `ShippingOption`: Shipping options

### 7. Third-Party Adapters (`server/thirdparty/`)

External services are integrated through adapters:

#### SinaliteAdapter
- Product catalog integration
- Pricing calculations
- Shipping estimates
- Order processing

#### MailerSendAdapter
- Email delivery service
- High deliverability
- Analytics and tracking
- Template support

#### SMTPAdapter
- Generic SMTP email service
- Gmail/Outlook/Yahoo support
- Local SMTP server support
- Fallback email option

#### SupabaseAdapter
- Cloud storage integration
- File upload/download
- Public URL generation
- File management

## Configuration Management

### Environment-Based Configuration

The application supports multiple environments:

#### Development (`DevelopmentConfig`)
- Debug mode enabled
- Local database
- Development API keys
- Detailed logging

#### Testing (`TestingConfig`)
- Test database
- Mock services
- Isolated test environment
- Fast test execution

#### Production (`ProductionConfig`)
- Optimized performance
- Production database
- Security hardening
- Error monitoring

### Configuration Files

- `server/config.py`: Configuration classes
- Environment variables: Runtime configuration
- `.env` files: Local development settings

## API Design

### RESTful Endpoints

The API follows RESTful conventions:

```
/api/auth/*          - Authentication endpoints
/api/pricing/*       - Pricing and product endpoints
/api/cart/*          - Shopping cart endpoints
/api/print/*         - Print product endpoints
/api/contact/*       - Contact form endpoints
```

### API Documentation

- **Swagger/OpenAPI**: Automatic API documentation
- **Interactive Documentation**: Test endpoints in browser
- **Schema Validation**: Request/response validation
- **Error Handling**: Standardized error responses

## Security Architecture

### Authentication & Authorization

- **JWT Tokens**: Stateless authentication
- **Role-Based Access Control**: Granular permissions
- **Password Security**: Bcrypt hashing
- **Session Management**: Secure session handling

### Data Protection

- **Input Validation**: Request data validation
- **SQL Injection Prevention**: Parameterized queries
- **CORS Configuration**: Cross-origin request handling
- **Environment Variables**: Secure credential storage

### Third-Party Security

- **API Key Management**: Secure third-party credentials
- **HTTPS Only**: Encrypted communications
- **Rate Limiting**: API abuse prevention
- **Audit Logging**: Security event tracking

## Database Architecture

### PostgreSQL Database

- **ACID Compliance**: Data integrity guarantees
- **Relational Design**: Normalized data structure
- **Migrations**: Version-controlled schema changes
- **Indexing**: Optimized query performance

### Database Models

#### User Management
- User accounts and profiles
- Authentication tokens
- Role and permission management
- Session tracking

#### Product Catalog
- Product information
- Categories and types
- Vendor management
- Product relationships

#### Pricing System
- Dynamic pricing
- Store-specific pricing
- Product variants
- Pricing history

#### Cart System
- Shopping cart persistence
- Cart item management
- Session-based carts
- Cart calculations

## File Storage Architecture

### Multi-Backend Support

The application supports multiple storage backends:

#### Local Storage
- File system storage
- Development environment
- Simple file management
- Local file serving

#### Supabase Storage
- Cloud storage integration
- CDN delivery
- Scalable file management
- Public URL generation

### File Management Features

- **Upload/Download**: File transfer operations
- **File Validation**: Type and size validation
- **Security**: Access control and permissions
- **Performance**: Optimized file serving

## Error Handling & Logging

### Error Handling Strategy

- **Centralized Error Handling**: Consistent error responses
- **Error Classification**: Different error types
- **User-Friendly Messages**: Clear error communication
- **Debug Information**: Detailed error logging

### Logging Architecture

- **Structured Logging**: JSON-formatted logs
- **Log Levels**: Debug, Info, Warning, Error
- **Context Information**: Request context tracking
- **Performance Monitoring**: Request timing and metrics

## Testing Architecture

### Test Organization

- **Unit Tests**: Individual component testing
- **Integration Tests**: Service integration testing
- **API Tests**: Endpoint testing
- **Mock Services**: Isolated testing

### Test Infrastructure

- **pytest**: Testing framework
- **Test Database**: Isolated test environment
- **Mock Objects**: External service mocking
- **Coverage Reporting**: Code coverage tracking

## Deployment Architecture

### Application Server

- **Gunicorn**: WSGI application server
- **Flask**: Web application framework
- **Process Management**: Multi-worker processes
- **Load Balancing**: Horizontal scaling support

### Database

- **PostgreSQL**: Primary database
- **Connection Pooling**: Optimized connections
- **Backup Strategy**: Data protection
- **Monitoring**: Performance tracking

### External Services

- **Sinalite API**: Product and pricing service
- **MailerSend/SMTP**: Email delivery service
- **Supabase**: Cloud storage service
- **CDN**: Content delivery network

## Performance Considerations

### Caching Strategy

- **Database Query Caching**: Reduced database load
- **API Response Caching**: Faster response times
- **Static Asset Caching**: CDN optimization
- **Session Caching**: Improved user experience

### Optimization Techniques

- **Database Indexing**: Query performance optimization
- **Lazy Loading**: Reduced memory usage
- **Connection Pooling**: Efficient resource usage
- **Async Operations**: Non-blocking operations

## Monitoring & Observability

### Application Monitoring

- **Health Checks**: Service availability monitoring
- **Performance Metrics**: Response time tracking
- **Error Tracking**: Error rate monitoring
- **Resource Usage**: Memory and CPU monitoring

### Business Metrics

- **User Activity**: User engagement tracking
- **API Usage**: Endpoint usage statistics
- **Error Rates**: Service reliability metrics
- **Performance Trends**: Long-term performance analysis

## Future Architecture Considerations

### Scalability

- **Microservices**: Service decomposition
- **API Gateway**: Centralized API management
- **Service Mesh**: Service communication
- **Container Orchestration**: Kubernetes deployment

### Technology Evolution

- **GraphQL**: Flexible API queries
- **Event-Driven Architecture**: Asynchronous processing
- **Real-time Features**: WebSocket integration
- **Machine Learning**: Intelligent features

This architecture provides a solid foundation for the Go Postal SD application, ensuring scalability, maintainability, and reliability while supporting future growth and feature development.
