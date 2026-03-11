from ninja import Router

router = Router()

@router.get("/hello")
def hello_sitemaps(request):
    return {
        "service": "Sitemap Generator",
        "status": "online",
        "message": "Hello from the sitemap module!"
    }