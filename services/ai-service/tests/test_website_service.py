from app.services.website_service import WebsiteContent, WebsiteService


def test_crawl_respects_same_domain_and_max_pages(monkeypatch) -> None:
    service = WebsiteService()

    pages = {
        "https://example.com/": WebsiteContent(
            url="https://example.com/",
            title="Home",
            text="home page",
            links=[
                "https://example.com/about",
                "https://other.com/news",
            ],
        ),
        "https://example.com/about": WebsiteContent(
            url="https://example.com/about",
            title="About",
            text="about page",
            links=["https://example.com/contact"],
        ),
        "https://example.com/contact": WebsiteContent(
            url="https://example.com/contact",
            title="Contact",
            text="contact page",
            links=[],
        ),
    }

    monkeypatch.setattr(service, "fetch", lambda url: pages[url])

    results = service.crawl("https://example.com", max_pages=2, same_domain_only=True)

    assert [item.url for item in results] == [
        "https://example.com/",
        "https://example.com/about",
    ]


def test_crawl_allows_cross_domain_when_disabled(monkeypatch) -> None:
    service = WebsiteService()

    pages = {
        "https://example.com/": WebsiteContent(
            url="https://example.com/",
            title="Home",
            text="home page",
            links=["https://other.com/news"],
        ),
        "https://other.com/news": WebsiteContent(
            url="https://other.com/news",
            title="News",
            text="news page",
            links=[],
        ),
    }

    monkeypatch.setattr(service, "fetch", lambda url: pages[url])

    results = service.crawl("https://example.com", max_pages=2, same_domain_only=False)

    assert [item.url for item in results] == [
        "https://example.com/",
        "https://other.com/news",
    ]
