# SupabaseAdapter Documentation

## Overview

The `SupabaseAdapter` is a third-party integration adapter that provides cloud storage capabilities using Supabase Storage. Supabase is a backend-as-a-service platform that offers PostgreSQL database, authentication, and storage services.

## Configuration

### Environment Variables

```bash
# Required - Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your_supabase_anon_key
SUPABASE_BUCKET=your_bucket_name
```

### Getting Supabase Credentials

1. **Create Project**: Sign up at [Supabase](https://supabase.com/)
2. **Create Storage Bucket**: 
   - Go to Storage in your Supabase dashboard
   - Create a new bucket (e.g., "uploads", "documents")
   - Set appropriate permissions (public/private)
3. **Get API Key**: Copy the anon/public key from Settings > API
4. **Get Project URL**: Copy the project URL from Settings > API

## Features

- **Cloud Storage**: Scalable file storage in the cloud
- **Public URLs**: Automatic generation of public file URLs
- **File Management**: Upload and delete files
- **Security**: Built-in access control and permissions
- **CDN**: Global content delivery network
- **Versioning**: File version management (if enabled)

## Core Functionality

### 1. File Upload

```python
from server.thirdparty.supabase import SupabaseAdapter

# Initialize adapter
supabase_adapter = SupabaseAdapter()
supabase_adapter.init_app(app)

# Upload file
with open('document.pdf', 'rb') as file:
    file_data = file.read()

public_url = supabase_adapter.upload_file(
    file_data=file_data,
    filename="document.pdf",
    content_type="application/pdf"
)

print(f"File uploaded: {public_url}")
```

### 2. File Deletion

```python
# Delete file using public URL
success = supabase_adapter.delete_file(
    file_path="https://your-project.supabase.co/storage/v1/object/public/uploads/document.pdf"
)

if success:
    print("File deleted successfully")
else:
    print("File deletion failed")
```

## Integration with FileStorageService

The SupabaseAdapter is designed to work with the FileStorageService:

```python
from server.services.file_storage_service import RemoteFileStorage

# Initialize remote file storage with Supabase
file_storage = RemoteFileStorage()
file_storage.init_app(app)

# Upload file
public_url = file_storage.upload_file(
    file_data=file_data,
    file_name="document.pdf",
    content_type="application/pdf"
)

# Delete file
success = file_storage.delete_file(public_url)
```

## File Upload Workflow

### 1. Basic Upload
```python
def upload_user_document(user_id, file_data, filename, content_type):
    """Upload user document to Supabase storage."""
    
    # Generate unique filename
    timestamp = int(time.time())
    unique_filename = f"{timestamp}_{filename}"
    
    # Upload to Supabase
    public_url = supabase_adapter.upload_file(
        file_data=file_data,
        filename=unique_filename,
        content_type=content_type
    )
    
    return {
        'success': True,
        'url': public_url,
        'filename': unique_filename
    }
```

### 2. File Validation
```python
def validate_and_upload_file(file_data, filename, content_type):
    """Validate file before uploading."""
    
    # File size validation (e.g., 10MB limit)
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_data) > max_size:
        return {'success': False, 'error': 'File too large'}
    
    # File type validation
    allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
    if content_type not in allowed_types:
        return {'success': False, 'error': 'File type not allowed'}
    
    # Upload file
    try:
        public_url = supabase_adapter.upload_file(
            file_data=file_data,
            filename=filename,
            content_type=content_type
        )
        return {'success': True, 'url': public_url}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

## Error Handling

The adapter handles various error scenarios:

### 1. Configuration Errors
- Missing Supabase credentials
- Invalid project URL or API key
- Bucket not found or inaccessible

### 2. Upload Errors
- File size limits exceeded
- Network connectivity issues
- Permission denied errors
- Invalid file format

### 3. Example Error Handling
```python
try:
    public_url = supabase_adapter.upload_file(
        file_data=file_data,
        filename=filename,
        content_type=content_type
    )
    return {'success': True, 'url': public_url}
except Exception as e:
    logger.error(f"Supabase upload failed: {str(e)}")
    return {'success': False, 'error': str(e)}
```

## File Management Patterns

### 1. User File Organization
```python
def upload_user_avatar(user_id, image_data):
    """Upload user avatar with organized naming."""
    
    filename = f"avatars/user_{user_id}_avatar.jpg"
    
    public_url = supabase_adapter.upload_file(
        file_data=image_data,
        filename=filename,
        content_type="image/jpeg"
    )
    
    return public_url
```

### 2. Document Management
```python
def upload_order_document(order_id, document_data, doc_type):
    """Upload order-related documents."""
    
    timestamp = int(time.time())
    filename = f"orders/{order_id}/{doc_type}_{timestamp}.pdf"
    
    public_url = supabase_adapter.upload_file(
        file_data=document_data,
        filename=filename,
        content_type="application/pdf"
    )
    
    return public_url
```

### 3. Temporary File Cleanup
```python
def cleanup_temp_files(temp_urls):
    """Clean up temporary files."""
    
    for url in temp_urls:
        try:
            supabase_adapter.delete_file(url)
            logger.info(f"Deleted temp file: {url}")
        except Exception as e:
            logger.error(f"Failed to delete temp file {url}: {e}")
```

## Security Considerations

### 1. Access Control
- Configure bucket permissions appropriately
- Use RLS (Row Level Security) policies
- Implement user-specific access controls
- Validate file types and sizes

### 2. File Validation
```python
def validate_upload_file(file_data, filename, content_type):
    """Comprehensive file validation."""
    
    # Size validation
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_data) > max_size:
        raise ValueError("File size exceeds limit")
    
    # Type validation
    allowed_types = {
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
        'application/pdf': ['.pdf']
    }
    
    if content_type not in allowed_types:
        raise ValueError("File type not allowed")
    
    # Extension validation
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in allowed_types[content_type]:
        raise ValueError("File extension mismatch")
    
    return True
```

### 3. Secure File Naming
```python
def generate_secure_filename(original_filename, user_id):
    """Generate secure filename to prevent conflicts."""
    
    # Sanitize filename
    safe_filename = secure_filename(original_filename)
    
    # Generate unique name
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    
    return f"{user_id}_{timestamp}_{unique_id}_{safe_filename}"
```

## Performance Optimization

### 1. File Size Limits
```python
# Configure appropriate limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5MB for images
MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20MB for documents
```

### 2. Compression for Images
```python
from PIL import Image
import io

def compress_image(image_data, max_size=1024):
    """Compress image before upload."""
    
    image = Image.open(io.BytesIO(image_data))
    
    # Resize if too large
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # Compress
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=85, optimize=True)
    
    return output.getvalue()
```

## Testing

### Unit Testing
```python
import unittest
from unittest.mock import patch, MagicMock
from server.thirdparty.supabase import SupabaseAdapter

class TestSupabaseAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = SupabaseAdapter()
        # Mock Flask app
        self.app = MagicMock()
        self.app.config = {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_API_KEY': 'test_key',
            'SUPABASE_BUCKET': 'test_bucket'
        }
    
    @patch('supabase.create_client')
    def test_upload_file_success(self, mock_create_client):
        # Mock successful upload
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        
        mock_create_client.return_value = mock_client
        mock_client.storage.from_.return_value = mock_bucket
        mock_bucket.upload.return_value = None
        mock_bucket.get_public_url.return_value = "https://test.supabase.co/storage/v1/object/public/test_bucket/test_file.jpg"
        
        self.adapter.init_app(self.app)
        
        result = self.adapter.upload_file(
            file_data=b"test data",
            filename="test_file.jpg",
            content_type="image/jpeg"
        )
        
        self.assertEqual(result, "https://test.supabase.co/storage/v1/object/public/test_bucket/test_file.jpg")
```

### Integration Testing
```python
def test_supabase_integration():
    """Test actual Supabase storage integration."""
    adapter = SupabaseAdapter()
    
    # Skip if not configured
    if not os.getenv('SUPABASE_URL'):
        pytest.skip("Supabase not configured")
    
    adapter.init_app(app)
    
    # Test upload
    test_data = b"test file content"
    public_url = adapter.upload_file(
        file_data=test_data,
        filename="test_file.txt",
        content_type="text/plain"
    )
    
    assert public_url.startswith("https://")
    assert "test_file.txt" in public_url
    
    # Test deletion
    success = adapter.delete_file(public_url)
    assert success == True
```

## Troubleshooting

### Common Issues

1. **"Bucket not found"**
   - Verify bucket name in Supabase dashboard
   - Check bucket permissions
   - Ensure bucket exists and is accessible

2. **"Authentication failed"**
   - Verify SUPABASE_URL and SUPABASE_API_KEY
   - Check API key permissions
   - Ensure project is active

3. **"Upload failed"**
   - Check file size limits
   - Verify file format is supported
   - Check network connectivity
   - Review Supabase storage quotas

4. **"Delete failed"**
   - Verify file URL format
   - Check file exists in storage
   - Ensure proper permissions

### Debug Steps

1. **Check Configuration**
   ```python
   adapter = SupabaseAdapter()
   adapter.init_app(app)
   print(f"Bucket: {adapter.bucket}")
   print(f"Client configured: {adapter.client is not None}")
   ```

2. **Test Supabase Connection**
   ```python
   from supabase import create_client
   
   try:
       client = create_client(
           os.getenv('SUPABASE_URL'),
           os.getenv('SUPABASE_API_KEY')
       )
       print("Supabase connection successful")
   except Exception as e:
       print(f"Supabase connection failed: {e}")
   ```

3. **Check Supabase Dashboard**
   - Log into Supabase dashboard
   - Check storage usage and quotas
   - Review file upload logs
   - Verify bucket permissions

## Best Practices

### 1. File Organization
- Use organized folder structure
- Implement consistent naming conventions
- Separate public and private files
- Use appropriate file extensions

### 2. Error Handling
- Always handle upload/deletion errors
- Implement retry logic for transient failures
- Log errors for monitoring
- Provide user-friendly error messages

### 3. Security
- Validate file types and sizes
- Use secure filename generation
- Implement proper access controls
- Regular security audits

### 4. Performance
- Compress images before upload
- Implement file size limits
- Use CDN for better performance
- Monitor storage usage

## Comparison with Local Storage

| Feature | Supabase Storage | Local Storage |
|---------|------------------|---------------|
| **Scalability** | Excellent | Limited |
| **Availability** | High | Depends on server |
| **Backup** | Automatic | Manual |
| **CDN** | Built-in | None |
| **Cost** | Pay per use | Server storage |
| **Setup** | Simple | Simple |
| **Security** | Built-in | Manual |

## Future Enhancements

Potential improvements for the SupabaseAdapter:

1. **Batch Operations**: Support for bulk file operations
2. **Image Processing**: Built-in image resizing and optimization
3. **File Versioning**: Automatic file version management
4. **Webhook Support**: Real-time file change notifications
5. **Advanced Permissions**: Fine-grained access control
6. **Analytics**: File usage and performance metrics
