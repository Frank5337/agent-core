import re
from collections import deque
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


NOISE_LINES = {
    "skip to content",
    "main navigation",
    "return to top",
    "search",
    "appearance",
    "menu",
    "导航",
    "搜索",
    "返回顶部",
    "本页内容",
}


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._title_parts: list[str] = []
        self._text_parts: list[str] = []
        self._links: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
            return

        if tag == "title":
            self._in_title = True
            return

        if tag != "a":
            return

        for name, value in attrs:
            if name == "href" and value:
                self._links.append(value.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return

        text = data.strip()
        if not text:
            return

        if self._in_title:
            self._title_parts.append(text)
        self._text_parts.append(text)

    @property
    def title(self) -> str:
        return " ".join(self._title_parts).strip()

    @property
    def text(self) -> str:
        return "\n".join(self._text_parts).strip()

    @property
    def links(self) -> list[str]:
        return self._links


@dataclass
class WebsiteContent:
    url: str
    title: str
    text: str
    links: list[str]


class WebsiteService:
    def fetch(self, url: str) -> WebsiteContent:
        html = self._fetch_html(url)
        parser = _VisibleTextParser()
        parser.feed(html)

        text = self._normalize_text(parser.text)
        if not text:
            raise ValueError("website content is empty")

        title = parser.title or self._default_title(url)
        return WebsiteContent(
            url=url,
            title=title[:150],
            text=text[:200000],
            links=self._normalize_links(url, parser.links),
        )

    def crawl(self, url: str, max_pages: int = 5, same_domain_only: bool = True) -> list[WebsiteContent]:
        if max_pages < 1:
            raise ValueError("max_pages must be greater than 0")

        queue: deque[str] = deque([self._normalize_url(url)])
        visited: set[str] = set()
        results: list[WebsiteContent] = []
        base_host = self._host(url)

        while queue and len(results) < max_pages:
            current = queue.popleft()
            if current in visited:
                continue

            visited.add(current)
            try:
                content = self.fetch(current)
            except ValueError:
                continue

            results.append(content)
            if len(results) >= max_pages:
                break

            for link in content.links:
                normalized = self._normalize_url(link)
                if normalized in visited or normalized in queue:
                    continue
                if same_domain_only and self._host(normalized) != base_host:
                    continue
                queue.append(normalized)

        if not results:
            raise ValueError("failed to fetch website")

        return results

    def _fetch_html(self, url: str) -> str:
        request = Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                )
            },
        )
        try:
            with urlopen(request, timeout=20) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return response.read().decode(charset, errors="ignore")
        except HTTPError as exc:
            raise ValueError(f"failed to fetch website: HTTP {exc.code}") from exc
        except URLError as exc:
            raise ValueError("failed to fetch website") from exc

    def _normalize_links(self, current_url: str, links: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()

        for link in links:
            absolute = urljoin(current_url, link)
            parsed = urlparse(absolute)
            if parsed.scheme not in {"http", "https"}:
                continue

            cleaned = parsed._replace(fragment="").geturl()
            if cleaned in seen:
                continue

            seen.add(cleaned)
            normalized.append(cleaned)

        return normalized

    def _normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("url must start with http or https")

        path = parsed.path or "/"
        cleaned = parsed._replace(path=path, fragment="")
        return cleaned.geturl()

    def _host(self, url: str) -> str:
        return urlparse(url).netloc.lower().strip()

    def _default_title(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc or "website"

    def _normalize_text(self, text: str) -> str:
        lines: list[str] = []
        previous = ""

        for raw_line in text.splitlines():
            line = re.sub(r"\s+", " ", raw_line).strip()
            if not line:
                continue
            if self._is_noise_line(line):
                continue
            if line == previous:
                continue

            lines.append(line)
            previous = line

        compact = "\n".join(lines)
        compact = re.sub(r"\n{3,}", "\n\n", compact)
        return compact.strip()

    def _is_noise_line(self, line: str) -> bool:
        normalized = line.lower().strip()
        if normalized in NOISE_LINES:
            return True
        if normalized.startswith("skip to ") or normalized.startswith("return to "):
            return True
        if len(normalized) <= 2 and not re.search(r"[\u4e00-\u9fff]", normalized):
            return True
        return False


website_service = WebsiteService()
