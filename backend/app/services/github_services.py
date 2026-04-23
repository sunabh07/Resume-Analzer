import httpx
import asyncio
import base64
import os 
from dotenv import load_dotenv
load_dotenv()
import logging
import re
    
GITHUB_TOKEN = os.getenv("GITHUB_PAT")  # 🔥 add your token

class GithubService:
    def __init__(self):
        self.github_token = GITHUB_TOKEN
        self.base_url = "https://api.github.com"

        self.headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }

        self.logger = logging.getLogger(__name__)
    

    def extract_github_links(self, text: str):

        # ✅ Non-capturing regex (VERY IMPORTANT)
        pattern = r'(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?'

        matches = re.findall(pattern, text)

        links = []

        for link in matches:
            # Normalize
            if not link.startswith("http"):
                link = "https://" + link

            # Remove trailing junk
            link = link.rstrip('.,);]')

            # 🔥 Strict validation (filters garbage)
            if not re.match(r'^https://(www\.)?github\.com/[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)?$', link):
                continue

            # Avoid empty/broken links
            if link in ["https://github.com", "https://github.com/"]:
                continue

            links.append(link)

        return list(set(links)) # remove duplicates
    # 🔹 Extract username and repo
    def extract_username_repo(self, url: str):
        try:
            parts = url.rstrip("/").split("/")

            if len(parts) >= 5:
                return parts[-2], parts[-1]  # username, repo

            return parts[-1], None

        except Exception as e:
            self.logger.error(f"Error extracting username/repo from URL {url}: {str(e)}")
            return None, None

    # 🔹 Fetch README summary
    async def fetch_readme_summary(self, client, owner, repo):
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/readme"
            res = await client.get(url, headers=self.headers)

            if res.status_code != 200:
                self.logger.warning(f"README not found for {owner}/{repo}")
                return ""

            content = res.json().get("content", "")
            decoded = base64.b64decode(content).decode("utf-8", errors="ignore")

            summary = decoded.strip().replace("\n", " ")[:300]
            return summary

        except Exception as e:
            self.logger.error(f"Error fetching README for {owner}/{repo}: {str(e)}")
            return ""

    # 🔹 Fetch repo details
    async def fetch_repo_details(self, client, owner, repo):
        try:
            repo_url = f"{self.base_url}/repos/{owner}/{repo}"

            repo_res, lang_res, readme_summary = await asyncio.gather(
                client.get(repo_url, headers=self.headers),
                client.get(f"{repo_url}/languages", headers=self.headers),
                self.fetch_readme_summary(client, owner, repo),
                return_exceptions=True
            )

            if isinstance(repo_res, Exception) or repo_res.status_code != 200:
                self.logger.error(f"Failed to fetch repo {owner}/{repo}")
                return None

            repo_data = repo_res.json()

            languages = {}
            if not isinstance(lang_res, Exception) and lang_res.status_code == 200:
                languages = lang_res.json()

            result = {
                "name": repo_data.get("name"),
                "url": repo_data.get("html_url"),
                "description": repo_data.get("description"),
                "stars": repo_data.get("stargazers_count"),
                "forks": repo_data.get("forks_count"),
                "languages": list(languages.keys()),
                "updated_at": repo_data.get("updated_at"),
                "readme_summary": readme_summary
            }

            self.logger.info(f"Fetched repo: {owner}/{repo}")
            return result

        except Exception as e:
            self.logger.error(f"Error in fetch_repo_details for {owner}/{repo}: {str(e)}")
            return None

    # 🔹 Main function
    async def fetch_all_github_data(self, github_links):
        results = []

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                tasks = []

                for link in github_links:
                    owner, repo = self.extract_username_repo(link)

                    if not owner:
                        continue

                    if repo:
                        # Direct repo
                        tasks.append(self.fetch_repo_details(client, owner, repo))

                    else:
                        # Profile → fetch repos
                        try:
                            url = f"{self.base_url}/users/{owner}/repos"
                            res = await client.get(
                                url,
                                headers=self.headers,
                                params={"per_page": 10, "sort": "updated"}
                            )

                            if res.status_code != 200:
                                self.logger.error(f"Failed to fetch repos for {owner}")
                                continue

                            repos = res.json()

                            # Limit to top 5 repos
                            for r in repos[:5]:
                                tasks.append(
                                    self.fetch_repo_details(client, owner, r["name"])
                                )

                        except Exception as e:
                            self.logger.error(f"Error fetching repos for {owner}: {str(e)}")

                # 🔥 Parallel execution
                responses = await asyncio.gather(*tasks, return_exceptions=True)

                for r in responses:
                    if isinstance(r, dict) and r:
                        results.append(r)

        except Exception as e:
            self.logger.error(f"Error in fetch_all_github_data: {str(e)}")

        self.logger.info(f"Total repos fetched: {len(results)}")
        return results