#!/usr/bin/env python3
"""
꽃 추천 AI 시스템 1차 개발 완료 보고서 PDF 생성 스크립트
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """필요한 의존성 확인"""
    try:
        import markdown
        import weasyprint
        print("✅ 필요한 라이브러리가 설치되어 있습니다.")
        return True
    except ImportError as e:
        print(f"❌ 필요한 라이브러리가 설치되지 않았습니다: {e}")
        print("다음 명령어로 설치해주세요:")
        print("pip install markdown weasyprint")
        return False

def install_dependencies():
    """의존성 설치"""
    print("📦 필요한 라이브러리를 설치합니다...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "markdown", "weasyprint", "jinja2"
        ])
        print("✅ 라이브러리 설치 완료!")
        return True
    except subprocess.CalledProcessError:
        print("❌ 라이브러리 설치 실패")
        return False

def create_html_template():
    """HTML 템플릿 생성"""
    return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>꽃 추천 AI 시스템 1차 개발 완료 보고서</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Noto Sans KR', sans-serif;
            line-height: 1.6;
            color: #333;
            background: white;
            font-size: 12px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
        }
        
        h1 {
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        
        h2 {
            font-size: 18px;
            font-weight: 600;
            color: #34495e;
            margin: 30px 0 15px 0;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }
        
        h3 {
            font-size: 14px;
            font-weight: 500;
            color: #2c3e50;
            margin: 20px 0 10px 0;
        }
        
        h4 {
            font-size: 13px;
            font-weight: 500;
            color: #34495e;
            margin: 15px 0 8px 0;
        }
        
        p {
            margin-bottom: 10px;
            text-align: justify;
        }
        
        ul, ol {
            margin: 10px 0 10px 20px;
        }
        
        li {
            margin-bottom: 5px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 11px;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        
        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
        }
        
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 15px 0;
            border-left: 4px solid #3498db;
        }
        
        pre code {
            background: none;
            padding: 0;
        }
        
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin: 15px 0;
            font-style: italic;
            color: #666;
        }
        
        .highlight {
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
        }
        
        .success {
            background-color: #d4edda;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #28a745;
            margin: 15px 0;
        }
        
        .info {
            background-color: #d1ecf1;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #17a2b8;
            margin: 15px 0;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .toc {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        
        .toc ul {
            list-style-type: none;
            margin: 0;
        }
        
        .toc li {
            margin: 5px 0;
        }
        
        .toc a {
            text-decoration: none;
            color: #3498db;
        }
        
        .header-info {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 10px;
            color: #666;
        }
        
        @media print {
            body {
                font-size: 11px;
            }
            
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 20px;
            }
            
            h2 {
                font-size: 16px;
            }
            
            h3 {
                font-size: 13px;
            }
            
            table {
                font-size: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-info">
            <h1>꽃 추천 AI 시스템 1차 개발 완료 보고서</h1>
            <p><strong>프로젝트명:</strong> 꽃 추천 AI 시스템 1차 개발</p>
            <p><strong>개발 기간:</strong> 2024년 8월 ~ 2024년 8월 (1개월)</p>
            <p><strong>보고서 작성일:</strong> 2024년 8월 30일</p>
        </div>
        
        {{ content }}
        
        <div class="footer">
            <p><strong>보고서 작성자:</strong> AI 개발팀</p>
            <p><strong>검토자:</strong> 프로젝트 매니저</p>
            <p><strong>승인자:</strong> CTO</p>
            <p><em>본 보고서는 꽃 추천 AI 시스템 1차 개발 프로젝트의 완료 보고서입니다.</em></p>
        </div>
    </div>
</body>
</html>
"""

def convert_markdown_to_html(markdown_content):
    """마크다운을 HTML로 변환"""
    import markdown
    
    # 마크다운 확장 설정
    extensions = [
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br'
    ]
    
    # 마크다운을 HTML로 변환
    html_content = markdown.markdown(markdown_content, extensions=extensions)
    return html_content

def generate_pdf():
    """PDF 생성"""
    try:
        from weasyprint import HTML
        from jinja2 import Template
        
        # 마크다운 파일 읽기
        markdown_file = Path("docs/complete_report.md")
        if not markdown_file.exists():
            print(f"❌ 마크다운 파일을 찾을 수 없습니다: {markdown_file}")
            return False
        
        print(f"📖 마크다운 파일을 읽는 중: {markdown_file}")
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 마크다운을 HTML로 변환
        print("🔄 마크다운을 HTML로 변환 중...")
        html_content = convert_markdown_to_html(markdown_content)
        
        # HTML 템플릿 생성
        template = Template(create_html_template())
        full_html = template.render(content=html_content)
        
        # 출력 디렉토리 생성
        output_dir = Path("docs/pdf")
        output_dir.mkdir(exist_ok=True)
        
        # PDF 파일 경로
        pdf_file = output_dir / "꽃추천AI시스템_1차개발_완료보고서.pdf"
        
        # HTML을 PDF로 변환
        print("🔄 HTML을 PDF로 변환 중...")
        HTML(string=full_html).write_pdf(pdf_file)
        
        print(f"✅ PDF 생성 완료: {pdf_file}")
        print(f"📄 파일 크기: {pdf_file.stat().st_size / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF 생성 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 꽃 추천 AI 시스템 1차 개발 완료 보고서 PDF 생성")
    print("=" * 60)
    
    # 의존성 확인
    if not check_dependencies():
        print("\n📦 의존성 설치를 시도합니다...")
        if not install_dependencies():
            return False
    
    # PDF 생성
    if generate_pdf():
        print("\n🎉 PDF 생성이 완료되었습니다!")
        print("📁 파일 위치: docs/pdf/꽃추천AI시스템_1차개발_완료보고서.pdf")
        return True
    else:
        print("\n❌ PDF 생성에 실패했습니다.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
