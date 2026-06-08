from .base import BaseSkill
import httpx


class WebSearchSkill(BaseSkill):
    name = "web_search"
    description = "联网搜索补充背景知识和最新资料"

    def execute(self, context: dict) -> dict:
        project = context['project']
        questions = list(project.questions.all())

        search_queries = [f"数学建模 {q.content[:50]}" for q in questions[:3]]
        if not search_queries:
            search_queries = [f"数学建模 {project.title[:80]}"]

        search_results = []

        with httpx.Client(timeout=None) as client:
            for query in search_queries[:3]:
                try:
                    search_url = f"https://html.duckduckgo.com/html/?q={query}"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    response = client.get(search_url, headers=headers)
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.text, 'html.parser')
                        results = soup.select('.result__body')
                        snippet = '\n'.join(
                            r.get_text(strip=True)[:200]
                            for r in results[:5]
                        )
                        search_results.append(f"搜索: {query}\n{snippet}")
                except Exception:
                    pass

        context['search_results'] = '\n'.join(search_results)
        return context
