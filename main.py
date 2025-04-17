import os
import json
from paper_search import PaperSearcher
from paper_analysis import PaperAnalyzer
from md_generator import MarkdownGenerator
import requests

# 출력 디렉토리 설정
OUTPUT_DIR = "output"

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
    
    def generate(self, prompt, model="gemma3"):
        """Ollama API를 사용하여 텍스트 생성"""
        url = f"{self.base_url}/api/generate"
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"Ollama API 오류: {response.status_code} - {response.text}")

def main():
    print("🔍 연구 에이전트를 시작합니다...")
    
    # 출력 디렉토리 생성
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"'{OUTPUT_DIR}' 디렉토리를 생성했습니다.")
    
    # 사용자 입력 받기
    topic = input("연구 주제를 입력하세요: ")
    initial_papers_input = input("초기 참고 논문들을 입력하세요 (여러 논문은 줄바꿈으로 구분): ")
    initial_papers = initial_papers_input.strip().split(',') if initial_papers_input.strip() else []
    
    print(initial_papers)
    
    # Ollama 클라이언트 초기화
    llm_client = OllamaClient()
    
    # 1단계: 논문 검색
    print("\n📚 관련 논문을 검색 중입니다...")
    searcher = PaperSearcher(output_dir=OUTPUT_DIR)
    papers = searcher.search_papers(topic, initial_papers)
    
    # 검색 결과 저장
    searcher.save_results("paper_results.json")
    print(f"✅ {len(papers)}개의 논문을 찾았습니다.")
    
    # 2단계: 논문 분석
    print("\n🧠 논문을 분석 중입니다...")
    analyzer = PaperAnalyzer(llm_client)
    
    # LLM으로 논문 정보 보강
    enriched_papers = analyzer.enrich_papers_with_llm(papers)
    
    # 연구 흐름 분석
    print("📊 연구 트렌드를 분석 중입니다...")
    trend_analysis = analyzer.analyze_research_trends(enriched_papers)
    
    # 3단계: 마크다운 생성
    print("\n📝 마크다운 문서를 생성 중입니다...")
    md_gen = MarkdownGenerator(output_dir=OUTPUT_DIR)
    
    # 문서 구조 생성
    md_gen.generate_header(f"'{topic}' 연구 주제 분석")
    md_gen.add_section("연구 개요", f"이 문서는 '{topic}' 주제에 관한 연구 논문들을 분석한 결과입니다.")
    md_gen.generate_papers_table(enriched_papers)
    
    # 시각화 추가
    md_gen.generate_trend_visualization(enriched_papers)
    
    # 트렌드 분석 결과 추가
    md_gen.add_section("연구 흐름 분석", trend_analysis)
    
    # 참고 문헌 추가
    md_gen.add_references(enriched_papers)
    
    # 마크다운 파일 저장
    md_gen.save_markdown("output.md")
    
    print(f"\n✨ 작업이 완료되었습니다! '{OUTPUT_DIR}' 디렉토리에서 결과 파일을 확인하세요.")

if __name__ == "__main__":
    main()
