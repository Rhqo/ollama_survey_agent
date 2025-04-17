import json
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl
import pandas as pd
import os

font_path = './fonts/NanumGothic.ttf'  
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

class MarkdownGenerator:
    def __init__(self, output_dir="output"):
        self.output = ""
        self.output_dir = output_dir
        
        # 출력 디렉토리가 없으면 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_header(self, title: str) -> None:
        """마크다운 헤더 생성"""
        self.output += f"# {title}\n\n"
    
    def add_section(self, title: str, content: str) -> None:
        """섹션 추가"""
        self.output += f"## {title}\n\n{content}\n\n"
    
    def generate_papers_table(self, papers: List[Dict[str, Any]]) -> None:
        """논문 목록을 표로 변환"""
        # 연도별로 정렬
        sorted_papers = sorted(papers, key=lambda x: x.get('year', 0) or 0, reverse=True)
        
        self.output += "## 주요 논문 목록\n\n"
        self.output += "| 제목 | 저자 | 연도 | 인용 수 | 링크 |\n"
        self.output += "|------|------|------|--------|------|\n"
        
        for paper in sorted_papers:
            title = paper.get('title', 'N/A')
            authors = paper.get('authors', 'N/A')
            year = paper.get('year', 'N/A')
            citations = paper.get('citations', 'N/A')
            url = paper.get('url', '')
            
            # URL이 있으면 마크다운 링크로 변환
            if url:
                title_with_link = f"[{title}]({url})"
            else:
                title_with_link = title
            
            self.output += f"| {title_with_link} | {authors} | {year} | {citations} | {url} |\n"
        
        self.output += "\n"
    
    def generate_trend_visualization(self, papers: List[Dict[str, Any]], filename: str = "research_trend.png") -> None:
        """연구 트렌드 시각화 생성 및 마크다운에 추가"""
        try:
            # 연도 데이터 추출 (None 값 제외)
            years = [paper.get('year', None) for paper in papers if paper.get('year')]
            
            if not years:
                self.output += "## 연구 트렌드 시각화\n\n시각화를 위한 충분한 연도 데이터가 없습니다.\n\n"
                return
            
            # 연도별 카운트
            year_counts = pd.Series(years).value_counts().sort_index()
            
            # 시각화
            plt.figure(figsize=(10, 6))
            year_counts.plot(kind='bar')
            plt.title('연도별 발행 논문 수', fontproperties=font_prop)
            plt.xlabel('연도', fontproperties=font_prop)
            plt.ylabel('논문 수', fontproperties=font_prop)
            plt.tight_layout()
            
            # 출력 디렉토리에 이미지 저장
            save_path = os.path.join(self.output_dir, filename)
            plt.savefig(save_path)
            
            # 마크다운에 이미지 추가 (상대 경로만 사용)
            self.output += f"## 연구 트렌드 시각화\n\n"
            self.output += f"![연도별 발행 논문 수]({filename})\n\n"
            
        except Exception as e:
            print(f"시각화 생성 중 오류 발생: {e}")
            self.output += "## 연구 트렌드 시각화\n\n시각화를 생성할 수 없습니다.\n\n"
    
    def add_references(self, papers: List[Dict[str, Any]]) -> None:
        """참고 문헌 목록 추가"""
        self.output += "## 참고 문헌\n\n"
        
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'N/A')
            authors = paper.get('authors', 'N/A')
            year = paper.get('year', 'N/A')
            url = paper.get('url', '')
            
            self.output += f"{i}. {authors} ({year}). {title}"
            if url:
                self.output += f". [링크]({url})"
            self.output += "\n"
        
        self.output += "\n"
    
    def save_markdown(self, filename: str = "output.md") -> None:
        """마크다운 파일로 저장"""
        # 출력 디렉토리에 저장
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.output)
        
        print(f"마크다운 파일이 {file_path}에 저장되었습니다.")
