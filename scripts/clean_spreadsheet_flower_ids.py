#!/usr/bin/env python3
"""
스프레드시트의 flower_id에서 불필요한 점(.) 제거하는 스크립트
"""

import requests
from typing import List, Dict

class SpreadsheetCleaner:
    def __init__(self):
        self.spreadsheet_url = "https://docs.google.com/spreadsheets/d/1HK3AA9yoJyPgObotVaXMLSAYccxoEtC9LmvZuCww5ZY/export?format=csv&gid=2100622490"
    
    def fetch_spreadsheet_data(self) -> List[Dict]:
        """구글 스프레드시트에서 데이터 가져오기"""
        try:
            response = requests.get(self.spreadsheet_url)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                print("❌ 스프레드시트 데이터가 충분하지 않음")
                return []
            
            headers = [h.strip().strip('"') for h in lines[0].split(',')]
            print(f"📋 스프레드시트 헤더: {headers}")
            
            data = []
            for line in lines[1:]:
                if line.strip():
                    # CSV 파싱
                    values = []
                    current_value = ""
                    in_quotes = False
                    
                    for char in line:
                        if char == '"':
                            in_quotes = not in_quotes
                        elif char == ',' and not in_quotes:
                            values.append(current_value.strip().strip('"'))
                            current_value = ""
                        else:
                            current_value += char
                    
                    values.append(current_value.strip().strip('"'))
                    
                    if len(values) >= len(headers):
                        row = dict(zip(headers, values))
                        data.append(row)
            
            print(f"✅ 스프레드시트에서 {len(data)}개 행 데이터 가져옴")
            return data
            
        except Exception as e:
            print(f"❌ 스프레드시트 데이터 가져오기 실패: {e}")
            return []
    
    def clean_flower_id(self, flower_id: str) -> str:
        """flower_id에서 불필요한 점(.) 제거"""
        if not flower_id:
            return flower_id
        
        # 점(.) 제거
        cleaned = flower_id.replace('.', '')
        
        # 연속된 하이픈 정리
        while '--' in cleaned:
            cleaned = cleaned.replace('--', '-')
        
        # 양 끝 하이픈 제거
        cleaned = cleaned.strip('-')
        
        return cleaned
    
    def analyze_flower_ids(self):
        """flower_id 분석 및 정리 제안"""
        print("🔍 flower_id 분석 시작...")
        
        # 스프레드시트 데이터 가져오기
        spreadsheet_data = self.fetch_spreadsheet_data()
        if not spreadsheet_data:
            return
        
        # flower_id 분석
        original_ids = []
        cleaned_ids = []
        changes = []
        
        for row in spreadsheet_data:
            flower_id = row.get('flower_id', '').strip()
            if flower_id and flower_id != '#N/A':
                original_ids.append(flower_id)
                cleaned_id = self.clean_flower_id(flower_id)
                cleaned_ids.append(cleaned_id)
                
                if flower_id != cleaned_id:
                    changes.append((flower_id, cleaned_id))
        
        print(f"\n📊 분석 결과:")
        print(f"   전체 flower_id: {len(original_ids)}개")
        print(f"   변경 필요: {len(changes)}개")
        
        if changes:
            print(f"\n🔧 변경될 flower_id 목록:")
            for original, cleaned in changes:
                print(f"   {original} → {cleaned}")
        
        # JavaScript 스크립트 생성
        self.generate_cleanup_script(changes)
    
    def generate_cleanup_script(self, changes: List[tuple]):
        """Google Sheets에서 실행할 JavaScript 스크립트 생성"""
        if not changes:
            print("\n✅ 변경할 flower_id가 없습니다!")
            return
        
        script_content = f"""
// Google Sheets에서 실행할 flower_id 정리 스크립트
function cleanFlowerIds() {{
    const sheet = SpreadsheetApp.getActiveSheet();
    const dataRange = sheet.getDataRange();
    const values = dataRange.getValues();
    
    // 헤더에서 flower_id 컬럼 찾기
    const headers = values[0];
    const flowerIdCol = headers.indexOf('flower_id');
    
    if (flowerIdCol === -1) {{
        Logger.log('flower_id 컬럼을 찾을 수 없습니다.');
        return;
    }}
    
    console.log('flower_id 컬럼 위치:', flowerIdCol + 1);
    
    // 변경 매핑
    const changes = {{
"""
        
        for original, cleaned in changes:
            script_content += f'        "{original}": "{cleaned}",\n'
        
        script_content += """    };
    
    let updateCount = 0;
    
    // 각 행 확인 및 업데이트
    for (let i = 1; i < values.length; i++) {
        const currentValue = values[i][flowerIdCol];
        
        if (changes[currentValue]) {
            // 셀 업데이트
            sheet.getRange(i + 1, flowerIdCol + 1).setValue(changes[currentValue]);
            console.log(`${currentValue} → ${changes[currentValue]}`);
            updateCount++;
        }
    }
    
    console.log(`총 ${updateCount}개 flower_id가 업데이트되었습니다.`);
    
    // 완료 메시지
    SpreadsheetApp.getUi().alert(`flower_id 정리 완료!\\n${updateCount}개 항목이 업데이트되었습니다.`);
}
"""
        
        # 스크립트 파일로 저장
        script_filename = "clean_flower_ids_script.js"
        with open(script_filename, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"\n✅ JavaScript 스크립트 생성: {script_filename}")
        print(f"\n📋 실행 방법:")
        print(f"1. 구글 스프레드시트 열기")
        print(f"2. 확장 프로그램 → Apps Script 클릭")
        print(f"3. {script_filename} 파일의 내용 복사하여 붙여넣기")
        print(f"4. cleanFlowerIds 함수 실행")

def main():
    """메인 실행 함수"""
    cleaner = SpreadsheetCleaner()
    
    print("🧹 스프레드시트 flower_id 정리")
    print("=" * 50)
    
    cleaner.analyze_flower_ids()

if __name__ == "__main__":
    main()
