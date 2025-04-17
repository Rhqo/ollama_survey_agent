import arxiv
import json
from scholarly import scholarly
import requests
import os
from typing import List, Dict, Any

class PaperSearcher:
    def __init__(self, output_dir="output"):
        self.papers = []
        self.output_dir = output_dir
        
        # 출력 디렉토리가 없으면 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def search_arxiv(self, query: str, max_results: int = 10) -> None:
        """arXiv에서 논문 검색"""
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        for result in client.results(search):
            paper = {
                "title": result.title,
                "authors": ", ".join(author.name for author in result.authors),
                "year": result.published.year,
                "abstract": result.summary,
                "url": result.pdf_url,
                "citations": None,
                "key_findings": None
            }
            self.papers.append(paper)
    
    def search_google_scholar(self, query: str, max_results: int = 10) -> None:
        """Google Scholar에서 논문 검색"""
        try:
            # scholarly 최신 API 사용
            search_query = scholarly.search_pubs(query)
            count = 0
            
            for result in search_query:
                if count >= max_results:
                    break
                
                try:
                    # 딕셔너리 접근 방식 사용 (. 접근자 대신 [] 사용)
                    paper = {
                        "title": result['bib'].get('title', '') if 'bib' in result else '',
                        "authors": result['bib'].get('author', '') if 'bib' in result else '',
                        "year": result['bib'].get('year') if 'bib' in result else None,
                        "abstract": result['bib'].get('abstract', '') if 'bib' in result else '',
                        "url": result['bib'].get('url', '') if 'bib' in result else '',
                        "citations": result.get('citedby', 0),
                        "key_findings": None
                    }
                    self.papers.append(paper)
                    count += 1
                except (KeyError, TypeError) as e:
                    print(f"검색 결과 처리 중 오류 발생: {e}")
        
        except Exception as e:
            print(f"Google Scholar 검색 중 오류 발생: {e}")
            # 대체 방법: 저자 검색을 통한 논문 검색
            try:
                self._search_by_authors(query, max_results)
            except Exception as e2:
                print(f"저자 검색을 통한 논문 검색 중 오류 발생: {e2}")
    
    def _search_by_authors(self, query: str, max_results: int = 10) -> None:
        """저자 검색을 통해 논문 찾기"""
        try:
            author_search = scholarly.search_author(query)
            author = next(author_search)
            author_filled = scholarly.fill(author)
            
            count = 0
            for pub in author_filled.get('publications', []):
                if count >= max_results:
                    break
                
                try:
                    # 논문 상세 정보 가져오기
                    pub_filled = scholarly.fill(pub)
                    
                    paper = {
                        "title": pub_filled['bib'].get('title', ''),
                        "authors": pub_filled['bib'].get('author', ''),
                        "year": pub_filled['bib'].get('year'),
                        "abstract": pub_filled['bib'].get('abstract', ''),
                        "url": pub_filled['bib'].get('url', ''),
                        "citations": pub_filled.get('citedby', 0),
                        "key_findings": None
                    }
                    self.papers.append(paper)
                    count += 1
                except (KeyError, TypeError) as e:
                    print(f"논문 상세 정보 처리 중 오류 발생: {e}")
        
        except StopIteration:
            print(f"'{query}'와 관련된 저자를 찾을 수 없습니다.")
        except Exception as e:
            print(f"저자 검색 중 오류 발생: {e}")
    
    def search_papers(self, topic: str, initial_papers: List[str]) -> List[Dict[str, Any]]:
        """주제와 초기 논문들을 바탕으로 검색 수행"""
        # 초기 논문들로 검색어 확장
        search_query = f"{topic} "
        if initial_papers:
            for paper in initial_papers:
                if paper.strip():
                    search_query += f" OR {paper.strip()}"
        
        # arXiv 검색
        print("- arXiv에서 논문 검색 중...")
        self.search_arxiv(search_query)
        
        # Google Scholar 검색
        print("- Google Scholar에서 논문 검색 중...")
        self.search_google_scholar(search_query)
        
        return self.papers
    
    def to_json(self) -> str:
        """논문 목록을 JSON 형식으로 변환"""
        return json.dumps({"papers": self.papers}, ensure_ascii=False, indent=2)
    
    def save_results(self, filename: str = "paper_results.json") -> None:
        """논문 검색 결과를 JSON 파일로 저장"""
        # 출력 디렉토리 내에 파일 저장
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        print(f"➡️ 논문 검색 결과를 {file_path}에 저장했습니다.")
