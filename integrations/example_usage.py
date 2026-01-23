"""
Example Usage of VARIOSYNC Cloud Integrations
Demonstrates how to use Supabase, Upstash Redis, Wasabi, and Modal in NiceGUI.
"""
import os
from nicegui import ui
from supabase import create_client
from integrations.upstash_client import UpstashRedisFactory
from integrations.wasabi_client import WasabiClientFactory
from integrations.modal_client import ModalClientFactory

# ============================================================================
# SUPABASE INTEGRATION
# ============================================================================

# Initialize Supabase clients
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")  # Safe for frontend
)

admin_supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Server-only, privileged
)


@ui.page("/auth")
def auth_page():
    """Example: Authentication with Supabase."""
    
    async def login():
        email = email_input.value
        password = password_input.value
        
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                ui.notify("Login successful!", type="positive")
                # Store user in session
                ui.open("/")
            else:
                ui.notify("Login failed", type="negative")
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
    
    with ui.card().classes("w-96 mx-auto mt-8"):
        ui.label("Login").classes("text-2xl font-bold mb-4")
        email_input = ui.input("Email", placeholder="user@example.com")
        password_input = ui.input("Password", password=True)
        ui.button("Login", on_click=login).classes("w-full mt-4")


# ============================================================================
# UPSTASH REDIS INTEGRATION
# ============================================================================

redis = UpstashRedisFactory.create_from_env()


@ui.page("/rate-limited")
def rate_limited_page():
    """Example: Rate limiting with Upstash Redis."""
    
    async def perform_action():
        # Get user ID from session (or IP)
        user_id = "user-123"  # In real app, get from session
        
        # Check rate limit (10 requests per 60 seconds)
        allowed, remaining = await redis.rate_limit(
            f"rate:{user_id}",
            limit=10,
            window=60
        )
        
        if not allowed:
            ui.notify(f"Rate limit exceeded! Try again later.", type="warning")
            return
        
        # Perform action
        ui.notify(f"Action performed! {remaining} requests remaining.", type="positive")
    
    with ui.card().classes("w-96 mx-auto mt-8"):
        ui.label("Rate Limited Action").classes("text-2xl font-bold mb-4")
        ui.label("Click button to test rate limiting (10 requests/minute)")
        ui.button("Perform Action", on_click=perform_action).classes("w-full mt-4")


@ui.page("/cache")
def cache_page():
    """Example: Caching with Upstash Redis."""
    
    async def get_cached_data():
        key = "cached_data"
        
        # Try to get from cache
        cached = await redis.cache_get(key)
        
        if cached:
            ui.notify("Data retrieved from cache!", type="info")
            result_label.text = f"Cached: {cached}"
        else:
            # Fetch from database
            data = {"message": "Hello from database!", "timestamp": "2024-01-15"}
            
            # Cache for 1 hour
            await redis.cache_set(key, data, ttl=3600)
            
            ui.notify("Data fetched and cached!", type="positive")
            result_label.text = f"Fresh: {data}"
    
    with ui.card().classes("w-96 mx-auto mt-8"):
        ui.label("Cache Example").classes("text-2xl font-bold mb-4")
        result_label = ui.label("Click to fetch data")
        ui.button("Get Data", on_click=get_cached_data).classes("w-full mt-4")


# ============================================================================
# WASABI INTEGRATION
# ============================================================================

wasabi = WasabiClientFactory.create_from_env()


@ui.page("/upload")
def upload_page():
    """Example: File upload with Wasabi presigned URLs."""
    
    async def generate_upload_url():
        if not wasabi:
            ui.notify("Wasabi not configured", type="warning")
            return
        
        filename = filename_input.value or "upload.csv"
        key = f"user-uploads/{filename}"
        
        try:
            # Generate presigned upload URL (valid for 1 hour)
            upload_url = wasabi.get_upload_url(
                key=key,
                expires_in=3600,
                content_type="text/csv"
            )
            
            # Display URL or redirect user
            url_label.text = f"Upload URL: {upload_url}"
            ui.notify("Upload URL generated!", type="positive")
            
            # Optionally open URL in new tab
            # ui.open(upload_url)
            
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
    
    async def generate_download_url():
        if not wasabi:
            ui.notify("Wasabi not configured", type="warning")
            return
        
        key = download_key_input.value
        
        try:
            # Generate presigned download URL
            download_url = wasabi.get_download_url(
                key=key,
                expires_in=3600
            )
            
            url_label.text = f"Download URL: {download_url}"
            ui.notify("Download URL generated!", type="positive")
            
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
    
    with ui.card().classes("w-96 mx-auto mt-8"):
        ui.label("Wasabi File Upload").classes("text-2xl font-bold mb-4")
        
        filename_input = ui.input("Filename", placeholder="file.csv")
        ui.button("Generate Upload URL", on_click=generate_upload_url).classes("w-full mt-4")
        
        ui.separator().classes("my-4")
        
        download_key_input = ui.input("File Key", placeholder="user-uploads/file.csv")
        ui.button("Generate Download URL", on_click=generate_download_url).classes("w-full mt-4")
        
        url_label = ui.label("").classes("mt-4 text-sm break-all")


# ============================================================================
# MODAL INTEGRATION
# ============================================================================

modal = ModalClientFactory.create_from_env()


@ui.page("/process")
def process_page():
    """Example: Trigger Modal serverless function."""
    
    async def trigger_processing():
        if not modal:
            ui.notify("Modal not configured", type="warning")
            return
        
        data = {"series_id": "AAPL", "action": "process"}
        
        try:
            # Trigger Modal function
            result = await modal.call_function_async(
                "heavy_process",
                data=data
            )
            
            ui.notify(f"Processing complete: {result}", type="positive")
            result_label.text = f"Result: {result}"
            
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
    
    with ui.card().classes("w-96 mx-auto mt-8"):
        ui.label("Modal Processing").classes("text-2xl font-bold mb-4")
        ui.label("Trigger heavy processing job on Modal")
        ui.button("Start Processing", on_click=trigger_processing).classes("w-full mt-4")
        result_label = ui.label("").classes("mt-4")


# ============================================================================
# COMBINED EXAMPLE: Upload → Process → Cache
# ============================================================================

@ui.page("/workflow")
def workflow_page():
    """Example: Complete workflow using all integrations."""
    
    async def run_workflow():
        # 1. Generate Wasabi upload URL
        if wasabi:
            upload_url = wasabi.get_upload_url("workflow/data.csv", expires_in=3600)
            ui.notify("Step 1: Upload URL generated", type="info")
        
        # 2. Check rate limit
        if redis:
            allowed, remaining = await redis.rate_limit("workflow:user-123", limit=5, window=60)
            if not allowed:
                ui.notify("Rate limit exceeded!", type="warning")
                return
            ui.notify(f"Step 2: Rate limit OK ({remaining} remaining)", type="info")
        
        # 3. Trigger Modal processing
        if modal:
            result = await modal.call_function_async("process_data", data={"file": "data.csv"})
            ui.notify(f"Step 3: Processing complete", type="info")
        
        # 4. Cache result
        if redis:
            await redis.cache_set("workflow:result", result, ttl=3600)
            ui.notify("Step 4: Result cached", type="info")
        
        ui.notify("Workflow complete!", type="positive")
    
    with ui.card().classes("w-96 mx-auto mt-8"):
        ui.label("Complete Workflow").classes("text-2xl font-bold mb-4")
        ui.label("Demonstrates: Upload → Rate Limit → Process → Cache")
        ui.button("Run Workflow", on_click=run_workflow).classes("w-full mt-4")
