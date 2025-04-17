import json
import os
from tqdm import tqdm
from typing import Dict, List, Any

class PaperAnalyzer:
    def __init__(self, llm_client):
        self.llm_client = llm_client  # Ollama 클라이언트
    
    def enrich_papers_with_llm(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """LLM을 사용하여 논문의 key_findings 필드 채우기"""
        enriched_papers = []
        
        for paper in tqdm(papers, desc="Analyzing", unit="paper"):
            if paper["abstract"]:
                prompt = f"""
                제목: {paper['title']}
                저자: {paper['authors']}
                요약: {paper['abstract']}

                위 논문의 핵심 발견점과 중요한 내용을 3-5개의 간결한 bullet point로 요약해 주세요.
                """
                
                # Ollama API 호출
                try:
                    response = self.llm_client.generate(prompt=prompt, model="gemma3")
                    paper["key_findings"] = response.strip()
                except Exception as e:
                    print(f"LLM 처리 중 오류 발생: {e}")
                    paper["key_findings"] = "데이터 처리 중 오류 발생"
            
            enriched_papers.append(paper)
        
        return enriched_papers
    
    def analyze_research_trends(self, papers: List[Dict[str, Any]]) -> str:
        """연구 트렌드 분석"""

        # 논문을 연도별로 정렬
        sorted_papers = sorted(papers, key=lambda x: x.get('year', 0) or 0)
        
        # 연구 트렌드 분석을 위한 프롬프트
        papers_info = "\n\n".join([
            f"제목: {p['title']}\n연도: {p['year']}\n저자: {p['authors']}\n요약: {p['abstract']}\n핵심 발견: {p['key_findings']}"
            for p in sorted_papers if p.get('abstract')
        ])
        
        prompt = f"""
        다음은 특정 연구 주제에 관한 논문 목록입니다:
        
        {papers_info}
        
        이 논문들을 바탕으로 다음 분석을 수행해 주세요:
        1. 시간 순서에 따른 연구 흐름 분석
        2. 주요 연구 방향과 패러다임 변화 식별
        3. 핵심 발견점과 혁신적 접근법 강조
        4. 연구 주제 발전 과정을 단계별로 명확히 구분
        5. 미래 연구 방향에 대한 제안
        
        마크다운 형식으로 체계적이고 상세한 분석 보고서를 작성해 주세요.
        """
        
        # Ollama API 호출
        try:
            response = self.llm_client.generate(prompt=prompt, model="deepseek-r1:1.5b")
            return response
        except Exception as e:
            print(f"연구 트렌드 분석 중 오류 발생: {e}")
            return "연구 트렌드 분석을 수행할 수 없습니다."
