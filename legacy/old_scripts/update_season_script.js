// 구글 스프레드시트 계절 정보 업데이트 스크립트
// 브라우저 개발자 도구에서 실행하세요

const seasonData = {
    "marguerite-daisy": "Spring/Summer 03-08",
    "bouvardia": "Spring/Summer 03-08",
    "alstroemeria-spp": "All Season 01-12",
    "alstroemeria-spp.": "All Season 01-12",
    "rose": "All Season 01-12",
    "tulip": "Spring 03-05",
    "gerbera-daisy": "All Season 01-12",
    "lily": "Summer 06-08",
    "carnation": "All Season 01-12",
    "dahlia": "Summer/Fall 06-11",
    "peony": "Spring 03-05",
    "garden-peony": "Spring 03-05",
    "iris": "Spring 03-05",
    "iris-sanguinea": "Spring 03-05",
    "anemone": "Spring 03-05",
    "anemone-coronaria": "Spring 03-05",
    "ranunculus": "Spring 03-05",
    "ranunculus-asiaticus": "Spring 03-05",
    "gladiolus": "Summer 06-08",
    "gladiolus-hortulanus": "Summer 06-08",
    "freesia": "Spring 03-05",
    "freesia-refracta": "Spring 03-05",
    "lisianthus": "All Season 01-12",
    "stock-flower": "Spring/Summer 03-08",
    "scabiosa": "Summer/Fall 06-11",
    "cockscomb": "Summer/Fall 06-11",
    "cotton-plant": "Fall 09-11",
    "drumstick-flower": "Summer/Fall 06-11",
    "gentiana": "Fall 09-11",
    "gentiana-andrewsii": "Fall 09-11",
    "zinnia-elegans": "Summer/Fall 06-11",
    "tagetes-erecta": "Summer/Fall 06-11",
    "veronica-spicata": "Summer/Fall 06-11",
    "lathyrus-odoratus": "Spring/Summer 03-08",
    "cymbidium-spp": "Winter/Spring 12-05",
    "cymbidium-spp.": "Winter/Spring 12-05",
    "hydrangea": "Summer 06-08",
    "astilbe": "Summer 06-08",
    "astilbe-japonica": "Summer 06-08",
    "anthurium": "All Season 01-12",
    "anthurium-andraeanum": "All Season 01-12",
    "babys-breath": "Spring/Summer 03-08",
    "oxypetalum": "Spring/Summer 03-08",
    "oxypetalum-coeruleum": "Spring/Summer 03-08",
    "iberis": "Spring 03-05",
    "iberis-sempervirens": "Spring 03-05",
    "ammi-majus": "Summer 06-08",
    "globe-amaranth": "Summer/Fall 06-11",
    "dianthus-caryophyllus": "All Season 01-12",
    "helianthus-annuus": "Summer/Fall 06-11",
    "phalaenopsis-aphrodite": "All Season 01-12",
    "eucalyptus-spp": "All Season 01-12",
    "callistephus-chinensis": "Summer/Fall 06-11",
    "spiraea-prunifolia": "Spring 03-05",
    "zantedeschia-aethiopica": "Spring/Summer 03-08",
    "campanula-medium": "Spring/Summer 03-08",
    "allium-cowanii": "Spring 03-05",
    "clematis-florida": "Spring/Summer 03-08"
};

// 스프레드시트 ID
const spreadsheetId = '1HK3AA9yoJyPgObotVaXMLSAYccxoEtC9LmvZuCww5ZY';
const sheetId = '2100622490';

// Google Sheets API 사용
async function updateSeasonInfo() {
    try {
        console.log("🔄 계절 정보 업데이트 시작...");
        
        // 현재 스프레드시트 데이터 가져오기
        const response = await gapi.client.sheets.spreadsheets.values.get({
            spreadsheetId: spreadsheetId,
            range: 'B2:B164'  // flower_id 컬럼 (B열)
        });

        const rows = response.result.values;
        const updates = [];

        rows.forEach((row, index) => {
            const flowerId = row[0];
            if (flowerId && flowerId !== '#N/A' && !flowerId.includes('written in expressive')) {
                // flower_id에서 기본 꽃 이름 추출 (색상 코드 제거)
                const parts = flowerId.split('-');
                let baseFlower = flowerId;
                
                if (parts.length >= 2) {
                    // 마지막 부분이 색상 코드인지 확인
                    const colorCodes = ['ll', 'pk', 'rd', 'wh', 'yl', 'pu', 'bl', 'or', 'gr', 'cr', 'be', 'iv'];
                    if (colorCodes.includes(parts[parts.length - 1])) {
                        baseFlower = parts.slice(0, -1).join('-');
                    }
                }
                
                const season = seasonData[baseFlower];
                if (season) {
                    updates.push({
                        range: `N${index + 2}`,  // N 컬럼 (season_months)
                        values: [[season]]
                    });
                    console.log(`행 ${index + 2}: ${flowerId} → ${season}`);
                }
            }
        });

        if (updates.length > 0) {
            await gapi.client.sheets.spreadsheets.values.batchUpdate({
                spreadsheetId: spreadsheetId,
                resource: {
                    valueInputOption: 'RAW',
                    data: updates
                }
            });
            console.log(`✅ ${updates.length}개 행 업데이트 완료`);
        } else {
            console.log("⚠️ 업데이트할 데이터가 없습니다.");
        }
    } catch (error) {
        console.error('❌ 업데이트 실패:', error);
    }
}

// 실행
console.log("🌸 구글 스프레드시트 계절 정보 업데이트 스크립트");
console.log("📋 사용 방법:");
console.log("1. 구글 스프레드시트를 열고 F12로 개발자 도구 열기");
console.log("2. Console 탭에서 이 스크립트를 복사하여 붙여넣기");
console.log("3. Enter 키를 눌러 실행");
console.log("");
console.log("🚀 스크립트를 실행하려면: updateSeasonInfo();");
