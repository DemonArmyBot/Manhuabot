from .scraper import Scraper
import json
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from loguru import logger
from .utitls import DEAULT_MSG_FORMAT


class AllMangaScraper(Scraper):

    def __init__(self):
        super().__init__()
        self.url = "https://allmanga.to"
        self.bg = None
        self.sf = "am"
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Referer": "https://allmanga.to/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        }
        self.search_query = dict()

    async def get_information(self, slug, data):
        url = f"https://allmanga.to/manga/{slug}"
        response = await self.get(url, cs=True, headers=self.headers)
        
        if response is None:
            return None

        soup = BeautifulSoup(response, "html.parser")
        
        # Extract title
        title_elem = soup.find("h1", {"class": "entry-title"})
        title = title_elem.text.strip() if title_elem else "N/A"
        
        # Extract cover/poster
        poster_elem = soup.find("div", {"class": "thumb"}).find("img") if soup.find("div", {"class": "thumb"}) else None
        poster = poster_elem.get("src") if poster_elem else "N/A"
        
        # Extract status
        status_elem = soup.find("span", string="Status")
        status = status_elem.find_next_sibling("span").text.strip() if status_elem else "N/A"
        
        # Extract genres
        genres_elems = soup.find("span", string="Genre")
        if genres_elems:
            genres_links = genres_elems.find_next_sibling("span").find_all("a")
            genres = ", ".join([genre.text.strip() for genre in genres_links])
        else:
            genres = "N/A"
        
        # Extract description/summary
        summary_elem = soup.find("div", {"class": "entry-content"})
        if summary_elem:
            # Remove unwanted elements from summary
            for elem in summary_elem.find_all(["script", "style", "div"]):
                elem.decompose()
            summary = summary_elem.get_text(strip=True)
        else:
            summary = "N/A"

        data['title'] = title
        data['poster'] = poster
        data['url'] = url

        data['msg'] = DEAULT_MSG_FORMAT.format(
            title=title,
            status=status,
            genres=genres,
            summary=summary[:200] + "..." if len(summary) > 200 else summary,
            url=url
        )

    async def search(self, query: str = ""):
        if query.lower() in self.search_query:
            return self.search_query[query.lower()]

        url = f"https://allmanga.to/?s={quote_plus(query)}&post_type=wp-manga"
        response = await self.get(url, cs=True, headers=self.headers)
        
        if response is None:
            return []

        soup = BeautifulSoup(response, "html.parser")
        mangas = []
        
        # Find all search result items
        results = soup.find_all("div", {"class": "row c-tabs-item__content"})
        
        for result in results:
            try:
                title_elem = result.find("h3").find("a")
                title = title_elem.text.strip()
                url = title_elem.get("href")
                slug = url.split("/")[-2] if url else None
                
                poster_elem = result.find("img")
                poster = poster_elem.get("src") if poster_elem else None
                
                # Extract latest chapter if available
                latest_chapter_elem = result.find("span", {"class": "font-meta chapter"})
                latest_chapter = latest_chapter_elem.find("a").text.strip() if latest_chapter_elem else "N/A"
                
                mangas.append({
                    "title": title,
                    "slug": slug,
                    "url": url,
                    "poster": poster,
                    "latest_chapter": latest_chapter
                })
            except Exception as e:
                logger.warning(f"Error parsing search result: {e}")
                continue

        self.search_query[query.lower()] = mangas
        return mangas

    async def get_chapters(self, data, page: int = 1):
        results = {}
        
        if 'slug' not in data:
            data['slug'] = data['url'].split("/")[-2] if data['url'] else None

        url = data['url'] if 'url' in data else f"https://allmanga.to/manga/{data['slug']}"
        
        response = await self.get(url, cs=True, headers=self.headers)
        if response is None:
            return None

        soup = BeautifulSoup(response, "html.parser")
        
        # Get manga information first
        await self.get_information(data['slug'], results)
        
        # Extract chapters
        chapters = []
        chapters_list = soup.find("ul", {"class": "wp-manga-chapter"})
        
        if chapters_list:
            chapter_elems = chapters_list.find_all("li")
            for chapter_elem in chapter_elems:
                try:
                    chapter_link = chapter_elem.find("a")
                    chapter_url = chapter_link.get("href")
                    chapter_title = chapter_link.text.strip()
                    
                    # Extract chapter number from title
                    import re
                    chapter_num_match = re.search(r'Chapter\s*(\d+(?:\.\d+)?)', chapter_title)
                    chapter_num = chapter_num_match.group(1) if chapter_num_match else "0"
                    
                    chapters.append({
                        "title": chapter_title,
                        "chap": chapter_num,
                        "hid": chapter_url.split("/")[-2],
                        "url": chapter_url
                    })
                except Exception as e:
                    logger.warning(f"Error parsing chapter: {e}")
                    continue

        results['chapters'] = chapters
        results['title'] = data.get('title', results.get('title', 'N/A'))
        results['url'] = url
        
        return results

    def iter_chapters(self, data, page=1):
        if not data or 'chapters' not in data:
            return []

        chapters_list = []
        for chapter in data['chapters']:
            title = chapter.get("title", f"Chapter {chapter.get('chap', 'N/A')}")
            
            chapters_list.append({
                "title": title,
                "url": chapter['url'],
                "slug": chapter['hid'],
                "manga_title": data['title'],
                "group_name": "AllManga",  # Default group name
                "poster": data.get('poster'),
            })

        return chapters_list

    async def get_pictures(self, url, data=None):
        response = await self.get(url, cs=True, headers=self.headers)
        if response is None:
            return []

        soup = BeautifulSoup(response, "html.parser")
        
        # Find all image containers
        images = []
        reading_content = soup.find("div", {"class": "reading-content"})
        
        if reading_content:
            img_elems = reading_content.find_all("img")
            for img_elem in img_elems:
                img_src = img_elem.get("src") or img_elem.get("data-src")
                if img_src:
                    images.append(img_src)
        
        return images
