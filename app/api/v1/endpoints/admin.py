from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any
import os
import json
import shutil
from pathlib import Path
from app.models.schemas import AdminResponse, FlowerInfo, FlowerDictionary, FlowerDictionarySearchRequest, FlowerDictionaryUpdateRequest, FlowerDictionaryResponse
import base64
from PIL import Image
import io
import sys

# 캘리그래피 동기화 서비스 import
try:
    from app.services.calli_sync import CalliImageSync
    CALLI_SYNC_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 캘리그래피 동기화 모듈을 불러올 수 없습니다: {e}")
    CALLI_SYNC_AVAILABLE = False

# 꽃 사전 서비스 import
try:
    from app.services.flower_dictionary import FlowerDictionaryService
    from app.services.flower_info_collector import FlowerInfoCollector
    FLOWER_DICT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 꽃 사전 모듈을 불러올 수 없습니다: {e}")
    FLOWER_DICT_AVAILABLE = False

router = APIRouter()

# 이미지 저장 경로
IMAGES_DIR = "data/images_webp"
FLOWER_DB_FILE = "data/flower_database.json"

@router.get("/flowers", response_model=List[FlowerInfo])
async def get_available_flowers():
    """사용 가능한 꽃 목록 조회"""
    try:
        # flower_matcher에서 꽃 데이터베이스 가져오기
        from app.services.flower_matcher import FlowerMatcher
        flower_matcher = FlowerMatcher()
        
        flowers = []
        flower_database = flower_matcher.flower_database
        
        for flower_name, flower_data in flower_database.items():
            # 폴더명 (flower_name을 하이픈으로 변환)
            folder = flower_name.lower().replace(' ', '-')
            folder_path = os.path.join(IMAGES_DIR, folder)
            
            # 실제 이미지 파일들 확인
            image_files = []
            if os.path.exists(folder_path):
                image_files = [f for f in os.listdir(folder_path) if f.endswith('.webp')]
            
            # 데이터베이스의 색상 정보 사용
            colors = flower_data.get('colors', [])
            if not colors:
                colors = ["화이트"]  # 기본값
            
            # 실제 이미지가 있으면 각 색상별로 별도 항목 생성
            if image_files:
                actual_colors = [f.replace('.webp', '') for f in image_files]
                for color in actual_colors:
                    images = [{"name": color, "url": f"/images/{folder}/{color}.webp"}]
                    flowers.append(FlowerInfo(
                        name=f"{flower_name}-{color}",
                        display_name=f"{flower_data.get('korean_name', flower_name)} ({color})",
                        colors=[color],
                        image_count=1,
                        images=images,
                        folder=folder,
                        default_color=color
                    ))
            else:
                # 실제 이미지가 없으면 데이터베이스 정보 사용
                for color in colors:
                    images = [{"name": color, "url": f"/images/{folder}/{color}.webp"}]
                    flowers.append(FlowerInfo(
                        name=f"{flower_name}-{color}",
                        display_name=f"{flower_data.get('korean_name', flower_name)} ({color})",
                        colors=[color],
                        image_count=1,
                        images=images,
                        folder=folder,
                        default_color=color
                    ))
        
        return sorted(flowers, key=lambda x: x.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-flower")
async def upload_flower_image(
    flower_name: str = Form(...),
    color: str = Form(...),
    image: UploadFile = File(...)
):
    """꽃 이미지 업로드"""
    try:
        # 폴더명 정규화 (공백을 하이픈으로)
        folder_name = flower_name.lower().replace(' ', '-')
        folder_path = os.path.join(IMAGES_DIR, folder_name)
        
        # 폴더 생성
        os.makedirs(folder_path, exist_ok=True)
        
        # 파일명 정규화
        color_name = color.strip()
        filename = f"{color_name}.webp"
        file_path = os.path.join(folder_path, filename)
        
        # 이미지 저장
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # 전체 시스템 자동 동기화
        await auto_sync()
        
        return {
            "success": True,
            "message": f"꽃 이미지 업로드 및 전체 동기화 완료: {flower_name} ({color})",
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-flowers-batch")
async def upload_flowers_batch(files: List[UploadFile] = File(...)):
    """일괄 꽃 이미지 업로드"""
    try:
        results = []
        errors = []
        
        for file in files:
            try:
                # 파일명에서 꽃 이름과 색상 추출 (예: "rose-red.webp" -> flower_name="rose", color="red")
                filename = file.filename
                if not filename.lower().endswith('.webp'):
                    errors.append(f"WebP 파일만 업로드 가능합니다: {filename}")
                    continue
                
                # 파일명에서 꽃 이름과 색상 추출
                name_without_ext = filename.replace('.webp', '')
                
                # 색상 패턴 매칭 (한국어/영어)
                color_patterns = {
                    'red': '레드', 'blue': '블루', 'yellow': '옐로우', 'white': '화이트', 
                    'pink': '핑크', 'purple': '퍼플', 'orange': '오렌지',
                    '레드': '레드', '블루': '블루', '옐로우': '옐로우', '화이트': '화이트',
                    '핑크': '핑크', '퍼플': '퍼플', '오렌지': '오렌지'
                }
                
                # 색상 찾기
                color = None
                flower_name = name_without_ext
                
                for pattern, korean_color in color_patterns.items():
                    if pattern.lower() in name_without_ext.lower():
                        color = korean_color
                        # 색상 부분 제거하여 꽃 이름 추출
                        flower_name = name_without_ext.lower().replace(pattern.lower(), '').strip('-_')
                        break
                
                if not color:
                    # 기본 색상으로 설정
                    color = '화이트'
                    flower_name = name_without_ext
                
                # 꽃 이름 정규화 (하이픈 제거, 공백으로 변환)
                flower_name = flower_name.replace('-', ' ').replace('_', ' ').strip()
                
                # 폴더명 정규화
                folder_name = flower_name.lower()
                folder_path = os.path.join(IMAGES_DIR, folder_name)
                
                # 폴더 생성
                os.makedirs(folder_path, exist_ok=True)
                
                # 파일 저장
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                results.append({
                    "filename": filename,
                    "flower_name": flower_name,
                    "color": color,
                    "file_path": file_path
                })
                
            except Exception as e:
                errors.append(f"파일 처리 실패: {filename} - {str(e)}")
        
        # 전체 시스템 자동 동기화
        if results:
            await auto_sync()
        
        return {
            "success": True,
            "message": f"일괄 업로드 완료: {len(results)}개 성공, {len(errors)}개 실패",
            "results": results,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== 꽃 사전 API 엔드포인트 =====

@router.get("/dictionary/flowers", response_model=List[FlowerDictionary])
async def get_flower_dictionary_list():
    """꽃 사전 목록 조회"""
    if not FLOWER_DICT_AVAILABLE:
        raise HTTPException(status_code=503, detail="꽃 사전 모듈을 사용할 수 없습니다.")
    
    try:
        service = FlowerDictionaryService()
        return service.get_all_flowers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dictionary/flowers/{flower_id}", response_model=FlowerDictionary)
async def get_flower_dictionary_detail(flower_id: str):
    """특정 꽃 사전 정보 조회"""
    if not FLOWER_DICT_AVAILABLE:
        raise HTTPException(status_code=503, detail="꽃 사전 모듈을 사용할 수 없습니다.")
    
    try:
        service = FlowerDictionaryService()
        flower = service.get_flower_info(flower_id)
        if not flower:
            raise HTTPException(status_code=404, detail="꽃을 찾을 수 없습니다")
        return flower
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dictionary/search", response_model=List[FlowerDictionary])
async def search_flower_dictionary(request: FlowerDictionarySearchRequest):
    """꽃 사전 검색"""
    if not FLOWER_DICT_AVAILABLE:
        raise HTTPException(status_code=503, detail="꽃 사전 모듈을 사용할 수 없습니다.")
    
    try:
        service = FlowerDictionaryService()
        return service.search_flowers(request.query, request.context, request.limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dictionary/collect-info")
async def collect_flower_info_from_llm(
    scientific_name: str = Form(...),
    korean_name: str = Form(...),
    color: str = Form(...)
):
    """LLM을 사용하여 꽃 정보 수집"""
    if not FLOWER_DICT_AVAILABLE:
        raise HTTPException(status_code=503, detail="꽃 사전 모듈을 사용할 수 없습니다.")
    
    try:
        # OpenAI API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API 키가 설정되지 않았습니다")
        
        collector = FlowerInfoCollector(api_key)
        flower_info = collector.collect_flower_info(scientific_name, korean_name, color)
        
        service = FlowerDictionaryService()
        flower_id = service.create_flower_entry(flower_info)
        
        return {
            "success": True,
            "message": f"꽃 정보 수집 완료: {flower_id}",
            "flower_id": flower_id,
            "data": flower_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dictionary/auto-expand")
async def auto_expand_flower_dictionary():
    """등록된 이미지 기준으로 꽃 사전 자동 확장"""
    if not FLOWER_DICT_AVAILABLE:
        raise HTTPException(status_code=503, detail="꽃 사전 모듈을 사용할 수 없습니다.")
    
    try:
        # 자동 확장 스크립트 실행
        import subprocess
        import sys
        
        result = subprocess.run([
            sys.executable, 
            "scripts/auto_expand_flower_dictionary.py"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": "꽃 사전 자동 확장 완료",
                "output": result.stdout
            }
        else:
            raise HTTPException(status_code=500, detail=f"자동 확장 실패: {result.stderr}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dictionary/batch-collect")
async def batch_collect_flower_info():
    """등록된 모든 꽃의 정보를 일괄 수집"""
    if not FLOWER_DICT_AVAILABLE:
        raise HTTPException(status_code=503, detail="꽃 사전 모듈을 사용할 수 없습니다.")
    
    try:
        # OpenAI API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API 키가 설정되지 않았습니다")
        
        # 등록된 꽃 목록 가져오기
        flower_matcher = FlowerMatcher()
        flower_list = []
        
        for flower_name, flower_data in flower_matcher.flower_database.items():
            for color in flower_data.get('colors', []):
                flower_list.append({
                    "scientific_name": flower_data.get('scientific_name', flower_name),
                    "korean_name": flower_data.get('korean_name', flower_name),
                    "color": color
                })
        
        collector = FlowerInfoCollector(api_key)
        created_ids = collector.batch_collect_flower_info(flower_list)
        
        return {
            "success": True,
            "message": f"일괄 정보 수집 완료: {len(created_ids)}개 꽃",
            "created_ids": created_ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/dictionary/flowers/{flower_id}")
async def update_flower_dictionary(flower_id: str, request: FlowerDictionaryUpdateRequest):
    """꽃 사전 정보 업데이트"""
    if not FLOWER_DICT_AVAILABLE:
        raise HTTPException(status_code=503, detail="꽃 사전 모듈을 사용할 수 없습니다.")
    
    try:
        service = FlowerDictionaryService()
        success = service.update_flower_info(flower_id, request.update_fields)
        
        if success:
            return {"success": True, "message": f"꽃 정보 업데이트 완료: {flower_id}"}
        else:
            raise HTTPException(status_code=404, detail="꽃을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/dictionary/flowers/{flower_id}")
async def delete_flower_dictionary(flower_id: str):
    """꽃 사전 정보 삭제"""
    if not FLOWER_DICT_AVAILABLE:
        raise HTTPException(status_code=503, detail="꽃 사전 모듈을 사용할 수 없습니다.")
    
    try:
        service = FlowerDictionaryService()
        success = service.delete_flower_entry(flower_id)
        
        if success:
            return {"success": True, "message": f"꽃 정보 삭제 완료: {flower_id}"}
        else:
            raise HTTPException(status_code=404, detail="꽃을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dictionary/metadata")
async def get_dictionary_metadata():
    """꽃 사전 메타데이터 조회"""
    if not FLOWER_DICT_AVAILABLE:
        raise HTTPException(status_code=503, detail="꽃 사전 모듈을 사용할 수 없습니다.")
    
    try:
        service = FlowerDictionaryService()
        return service.get_metadata()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-flower/{flower_name}")
async def delete_flower(flower_name: str):
    """꽃 폴더 삭제"""
    try:
        folder_path = os.path.join(IMAGES_DIR, flower_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            # flower_matcher.py에서도 제거
            await remove_from_flower_matcher(flower_name)
            return {"success": True, "message": f"꽃 삭제 성공: {flower_name}"}
        else:
            raise HTTPException(status_code=404, detail="꽃을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calligraphy/list")
async def get_calligraphy_list():
    """등록된 꽃 캘리그래피 목록 조회"""
    if not CALLI_SYNC_AVAILABLE:
        raise HTTPException(status_code=503, detail="캘리그래피 동기화 모듈을 사용할 수 없습니다.")
    
    try:
        syncer = CalliImageSync()
        return syncer.get_calligraphy_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calligraphy/sync")
async def sync_calligraphy_images():
    """꽃 캘리그래피 이미지 동기화"""
    if not CALLI_SYNC_AVAILABLE:
        raise HTTPException(status_code=503, detail="캘리그래피 동기화 모듈을 사용할 수 없습니다.")
    
    try:
        syncer = CalliImageSync()
        syncer.sync_images()
        
        # 결과 반환
        calli_list = syncer.get_calligraphy_list()
        return {
            "success": True,
            "message": f"캘리그래피 이미지 동기화 완료: {calli_list['total_count']}개 파일",
            "data": calli_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calligraphy/flower/{flower_name}")
async def get_flower_calligraphy(flower_name: str):
    """특정 꽃의 캘리그래피 이미지 경로 조회"""
    if not CALLI_SYNC_AVAILABLE:
        raise HTTPException(status_code=503, detail="캘리그래피 동기화 모듈을 사용할 수 없습니다.")
    
    try:
        syncer = CalliImageSync()
        calli_path = syncer.get_flower_calligraphy(flower_name)
        
        if calli_path:
            return {
                "success": True,
                "flower_name": flower_name,
                "calligraphy_path": calli_path
            }
        else:
            raise HTTPException(status_code=404, detail=f"{flower_name}의 캘리그래피를 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calligraphy/upload")
async def upload_calligraphy_image(
    flower_name: str = Form(...),
    file: UploadFile = File(...)
):
    """수동으로 꽃 캘리그래피 이미지 업로드"""
    if not CALLI_SYNC_AVAILABLE:
        raise HTTPException(status_code=503, detail="캘리그래피 동기화 모듈을 사용할 수 없습니다.")
    
    try:
        # 파일 확장자 검증
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다 (PNG, JPG, JPEG, GIF)")
        
        # 파일 크기 검증 (5MB 이하)
        if file.size and file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="파일 크기는 5MB 이하여야 합니다")
        
        syncer = CalliImageSync()
        result = syncer.upload_manual_image(flower_name, file)
        
        return {
            "success": True,
            "message": f"{flower_name} 캘리그래피 이미지 업로드 완료",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calligraphy/upload-batch")
async def upload_calligraphy_batch(files: List[UploadFile] = File(...)):
    """일괄 캘리그래피 이미지 업로드"""
    if not CALLI_SYNC_AVAILABLE:
        raise HTTPException(status_code=503, detail="캘리그래피 동기화 모듈을 사용할 수 없습니다.")
    
    try:
        syncer = CalliImageSync()
        results = []
        errors = []
        
        for file in files:
            try:
                # 파일명에서 꽃 이름 추출
                flower_name = syncer.extract_flower_name_from_filename(file.filename)
                if not flower_name:
                    errors.append(f"파일명에서 꽃 이름을 추출할 수 없습니다: {file.filename}")
                    continue
                
                # 파일 확장자 검증
                if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    errors.append(f"이미지 파일만 업로드 가능합니다: {file.filename}")
                    continue
                
                # 파일 크기 검증 (5MB 이하)
                file_size = 0
                try:
                    content = file.file.read()
                    file_size = len(content)
                    file.file.seek(0)  # 파일 포인터를 처음으로 되돌리기
                except Exception as e:
                    errors.append(f"파일 읽기 실패: {file.filename} - {str(e)}")
                    continue
                
                if file_size > 5 * 1024 * 1024:
                    errors.append(f"파일 크기는 5MB 이하여야 합니다: {file.filename}")
                    continue
                
                result = syncer.upload_manual_image(flower_name, file)
                results.append(result)
                
            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")
        
        return {
            "success": True,
            "message": f"일괄 업로드 완료: {len(results)}개 성공, {len(errors)}개 실패",
            "data": {
                "successful": results,
                "errors": errors
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/calligraphy/{flower_name}")
async def delete_calligraphy_image(flower_name: str):
    """특정 꽃의 캘리그래피 이미지 삭제"""
    if not CALLI_SYNC_AVAILABLE:
        raise HTTPException(status_code=503, detail="캘리그래피 동기화 모듈을 사용할 수 없습니다.")
    
    try:
        syncer = CalliImageSync()
        result = syncer.delete_manual_image(flower_name)
        
        return {
            "success": True,
            "message": f"{flower_name} 캘리그래피 이미지 삭제 완료",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/calligraphy/dummy/clear")
async def clear_dummy_calligraphy():
    """더미 캘리그래피 데이터 모두 삭제"""
    if not CALLI_SYNC_AVAILABLE:
        raise HTTPException(status_code=503, detail="캘리그래피 동기화 모듈을 사용할 수 없습니다.")
    
    try:
        syncer = CalliImageSync()
        result = syncer.clear_dummy_data()
        
        return {
            "success": True,
            "message": "더미 캘리그래피 데이터 삭제 완료",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scan-images")
async def scan_images():
    """이미지 폴더 스캔 및 DB 동기화"""
    try:
        flowers = []
        if os.path.exists(IMAGES_DIR):
            for folder in os.listdir(IMAGES_DIR):
                folder_path = os.path.join(IMAGES_DIR, folder)
                if os.path.isdir(folder_path):
                    # 폴더 내 이미지 파일들 확인
                    image_files = [f for f in os.listdir(folder_path) if f.endswith('.webp')]
                    if image_files:
                        colors = [f.replace('.webp', '') for f in image_files]
                        flowers.append({
                            "name": folder,
                            "display_name": folder.replace('-', ' ').title(),
                            "colors": colors,
                            "image_count": len(image_files)
                        })
        
        # flower_matcher.py 완전 동기화
        await sync_flower_matcher(flowers)
        
        return {"success": True, "message": f"이미지 스캔 및 완전 동기화 완료: {len(flowers)}개 꽃", "flowers": flowers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-sync")
async def auto_sync():
    """자동 동기화 - 모든 시스템 업데이트"""
    try:
        # 1. 이미지 폴더 스캔
        flowers = []
        if os.path.exists(IMAGES_DIR):
            for folder in os.listdir(IMAGES_DIR):
                folder_path = os.path.join(IMAGES_DIR, folder)
                if os.path.isdir(folder_path):
                    image_files = [f for f in os.listdir(folder_path) if f.endswith('.webp')]
                    if image_files:
                        colors = [f.replace('.webp', '') for f in image_files]
                        flowers.append({
                            "name": folder,
                            "display_name": folder.replace('-', ' ').title(),
                            "colors": colors,
                            "image_count": len(image_files)
                        })
        
        # 2. flower_matcher.py 완전 동기화
        await sync_flower_matcher(flowers)
        
        # 3. base64_images.json 업데이트 (필요한 경우)
        await update_base64_images()
        
        return {
            "success": True, 
            "message": f"자동 동기화 완료: {len(flowers)}개 꽃, 모든 시스템 업데이트됨",
            "flowers": flowers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-spreadsheet")
async def sync_spreadsheet():
    """구글 스프레드시트와 flower_matcher.py 동기화"""
    try:
        from scripts.sync_flower_database import FlowerDatabaseSync
        
        syncer = FlowerDatabaseSync()
        success = syncer.sync()
        
        if success:
            return {
                "success": True,
                "message": "스프레드시트 동기화 완료",
                "status": "success"
            }
        else:
            raise HTTPException(status_code=500, detail="스프레드시트 동기화 실패")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/full-sync")
async def full_sync():
    """전체 동기화: 스프레드시트 + 이미지 + flower_matcher + base64"""
    try:
        # 1. 스프레드시트 동기화
        from scripts.sync_flower_database import FlowerDatabaseSync
        syncer = FlowerDatabaseSync()
        spreadsheet_sync = syncer.sync()
        
        # 2. 이미지 폴더 스캔
        flowers = []
        if os.path.exists(IMAGES_DIR):
            for folder in os.listdir(IMAGES_DIR):
                folder_path = os.path.join(IMAGES_DIR, folder)
                if os.path.isdir(folder_path):
                    image_files = [f for f in os.listdir(folder_path) if f.endswith('.webp')]
                    if image_files:
                        colors = [f.replace('.webp', '') for f in image_files]
                        flowers.append({
                            "name": folder,
                            "display_name": folder.replace('-', ' ').title(),
                            "colors": colors,
                            "image_count": len(image_files)
                        })
        
        # 3. flower_matcher.py 완전 동기화
        await sync_flower_matcher(flowers)
        
        # 4. base64_images.json 업데이트
        await update_base64_images()
        
        return {
            "success": True,
            "message": "전체 동기화 완료",
            "spreadsheet_sync": spreadsheet_sync,
            "flowers": flowers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-google-drive")
async def sync_google_drive():
    """구글 드라이브 동기화"""
    try:
        from scripts.google_drive_api_sync import GoogleDriveAPISync
        
        syncer = GoogleDriveAPISync()
        success = syncer.sync()
        
        if success:
            return {
                "success": True,
                "message": "구글 드라이브 동기화 완료",
                "stats": syncer.stats
            }
        else:
            raise HTTPException(status_code=500, detail="구글 드라이브 동기화 실패")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-drive-watch")
async def start_drive_watch():
    """구글 드라이브 모니터링 시작"""
    try:
        import subprocess
        import sys
        
        # 백그라운드에서 모니터링 프로세스 시작
        script_path = os.path.join(os.getcwd(), "scripts", "google_drive_api_sync.py")
        process = subprocess.Popen([
            sys.executable, script_path, "--watch", "--interval", "300"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return {
            "success": True,
            "message": "구글 드라이브 모니터링이 시작되었습니다",
            "pid": process.pid
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-drive-watch")
async def stop_drive_watch():
    """구글 드라이브 모니터링 중단"""
    try:
        import subprocess
        
        # 모니터링 프로세스 종료
        subprocess.run(["pkill", "-f", "google_drive_api_sync.py"], 
                      capture_output=True, text=True)
        
        return {
            "success": True,
            "message": "구글 드라이브 모니터링이 중단되었습니다"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scan-raw-images")
async def scan_raw_images():
    """Raw 이미지 폴더 스캔"""
    try:
        raw_images_dir = "data/images_raw"
        raw_flowers = []
        
        if os.path.exists(raw_images_dir):
            for file in os.listdir(raw_images_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(raw_images_dir, file)
                    file_size = os.path.getsize(file_path)
                    
                    # 파일명에서 꽃 이름과 색상 추출
                    filename_without_ext = os.path.splitext(file)[0]
                    parts = filename_without_ext.split('_')
                    
                    if len(parts) >= 2:
                        flower_name = parts[0]
                        color = parts[1] if len(parts) > 1 else "Unknown"
                    else:
                        flower_name = filename_without_ext
                        color = "Unknown"
                    
                    raw_flowers.append({
                        "filename": file,
                        "flower_name": flower_name,
                        "color": color,
                        "file_size": file_size,
                        "file_path": file_path,
                        "webp_exists": False
                    })
        
        # WebP 변환 여부 확인
        for flower in raw_flowers:
            webp_path = os.path.join(IMAGES_DIR, flower["flower_name"].lower().replace(' ', '-'), f"{flower['color']}.webp")
            flower["webp_exists"] = os.path.exists(webp_path)
        
        return {"success": True, "raw_flowers": raw_flowers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert-raw-to-webp")
async def convert_raw_to_webp():
    """Raw 이미지를 WebP로 일괄 변환"""
    try:
        raw_images_dir = "data/images_raw"
        converted_count = 0
        errors = []
        
        if not os.path.exists(raw_images_dir):
            return {"success": False, "message": "Raw 이미지 폴더가 존재하지 않습니다."}
        
        for file in os.listdir(raw_images_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    file_path = os.path.join(raw_images_dir, file)
                    filename_without_ext = os.path.splitext(file)[0]
                    parts = filename_without_ext.split('_')
                    
                    if len(parts) >= 2:
                        flower_name = parts[0]
                        color = parts[1] if len(parts) > 1 else "Unknown"
                    else:
                        flower_name = filename_without_ext
                        color = "Unknown"
                    
                    # WebP 저장 경로
                    folder_name = flower_name.lower().replace(' ', '-')
                    folder_path = os.path.join(IMAGES_DIR, folder_name)
                    os.makedirs(folder_path, exist_ok=True)
                    
                    webp_path = os.path.join(folder_path, f"{color}.webp")
                    
                    # 이미 WebP가 존재하면 건너뛰기
                    if os.path.exists(webp_path):
                        continue
                    
                    # 이미지 변환
                    with Image.open(file_path) as img:
                        # RGBA를 RGB로 변환 (필요한 경우)
                        if img.mode == 'RGBA':
                            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                            rgb_img.paste(img, mask=img.split()[-1])
                            img = rgb_img
                        
                        img.save(webp_path, 'WEBP', quality=85)
                        converted_count += 1
                        
                except Exception as e:
                    errors.append(f"{file}: {str(e)}")
        
        return {
            "success": True, 
            "message": f"{converted_count}개 파일이 WebP로 변환되었습니다.",
            "converted_count": converted_count,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert-to-webp")
async def convert_to_webp(image: UploadFile = File(...), filename: str = Form(...)):
    """이미지를 WebP 형식으로 변환"""
    try:
        # 이미지 읽기
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data))
        
        # RGBA 모드인 경우 RGB로 변환
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # WebP로 변환
        webp_buffer = io.BytesIO()
        img.save(webp_buffer, format='WEBP', quality=85)
        webp_buffer.seek(0)
        
        # 파일명을 WebP로 변경
        name_without_ext = os.path.splitext(filename)[0]
        webp_filename = f"{name_without_ext}.webp"
        
        # WebP 파일 생성
        webp_file = UploadFile(
            filename=webp_filename,
            file=webp_buffer,
            content_type="image/webp"
        )
        
        return {
            "success": True,
            "message": f"WebP 변환 완료: {webp_filename}",
            "filename": webp_filename,
            "file": webp_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WebP 변환 실패: {str(e)}")

async def update_flower_matcher(flower_name: str, color: str):
    """flower_matcher.py에 새로운 꽃/색상 추가"""
    try:
        # flower_matcher.py 파일 읽기
        matcher_file = "app/services/flower_matcher.py"
        with open(matcher_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 꽃 이름을 표준 형식으로 변환 (예: babys-breath -> Babys Breath)
        display_name = flower_name.replace('-', ' ').title()
        
        # flower_database에 추가
        if f'"{display_name}":' not in content:
            # flower_database 딕셔너리에 새 항목 추가
            new_flower_entry = f'''            "{display_name}": {{
                "korean_name": "{display_name}",
                "scientific_name": "{display_name}",
                "image_url": self.base64_images.get("{flower_name}", {{}}).get("{color}", ""),
                "keywords": ["아름다움", "자연스러움"],
                "colors": ["{color}"],
                "emotions": ["아름다움", "자연스러움"]
            }},'''
            
            # 마지막 꽃 항목 다음에 추가
            content = content.replace('            "Ranunculus": {', f'{new_flower_entry}\n            "Ranunculus": {{')
        
        # available_colors에 추가
        if f'"{flower_name}":' not in content:
            new_color_entry = f'                "{flower_name}": ["{color}"],'
            content = content.replace('                "ranunculus": ["핑크", "화이트", "옐로우", "오렌지"]', 
                                    f'{new_color_entry}\n                "ranunculus": ["핑크", "화이트", "옐로우", "오렌지"]')
        
        # _get_flower_folder에 추가
        if f'"{display_name}": "{flower_name}"' not in content:
            new_folder_entry = f'            "{display_name}": "{flower_name}",'
            content = content.replace('            "Ranunculus": "ranunculus"', 
                                    f'{new_folder_entry}\n            "Ranunculus": "ranunculus"')
        
        # 파일 저장
        with open(matcher_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ flower_matcher.py 업데이트 완료: {flower_name} ({color})")
        
    except Exception as e:
        print(f"❌ flower_matcher.py 업데이트 실패: {e}")

async def remove_from_flower_matcher(flower_name: str):
    """flower_matcher.py에서 꽃 제거 후 전체 동기화"""
    try:
        print(f"🔄 flower_matcher.py에서 {flower_name} 제거 및 전체 동기화 시작")
        
        # 꽃 폴더 삭제 후 전체 동기화 수행
        await auto_sync()
        
        print(f"✅ {flower_name} 제거 및 전체 동기화 완료")
        
    except Exception as e:
        print(f"❌ flower_matcher.py 제거 실패: {e}")
        raise e

async def sync_flower_matcher(flowers: List[Dict]):
    """flower_matcher.py와 이미지 폴더 완전 동기화"""
    try:
        print(f"🔄 flower_matcher.py 완전 동기화 시작: {len(flowers)}개 꽃")
        
        # flower_matcher.py 파일 읽기
        matcher_file = "app/services/flower_matcher.py"
        with open(matcher_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 새로운 flower_database 딕셔너리 생성
        new_flower_database = {}
        
        for flower in flowers:
            flower_name = flower["name"]
            colors = flower["colors"]
            display_name = flower_name.replace('-', ' ').title()
            
            # 기본 정보 설정
            korean_name = display_name
            scientific_name = display_name
            
            # 특별한 경우 처리
            if flower_name == "babys-breath":
                korean_name = "베이비스브레스"
                scientific_name = "Gypsophila paniculata"
            elif flower_name == "garden-peony":
                korean_name = "작약"
                scientific_name = "Paeonia lactiflora"
            elif flower_name == "gerbera-daisy":
                korean_name = "거베라"
                scientific_name = "Gerbera jamesonii"
            elif flower_name == "globe-amaranth":
                korean_name = "천일홍"
                scientific_name = "Gomphrena globosa"
            elif flower_name == "cockscomb":
                korean_name = "맨드라미"
                scientific_name = "Celosia cristata"
            elif flower_name == "drumstick-flower":
                korean_name = "드럼스틱플라워"
                scientific_name = "Craspedia globosa"
            elif flower_name == "cotton-plant":
                korean_name = "목화"
                scientific_name = "Gossypium"
            elif flower_name == "marguerite-daisy":
                korean_name = "마가렛데이지"
                scientific_name = "Argyranthemum frutescens"
            elif flower_name == "stock-flower":
                korean_name = "스톡플라워"
                scientific_name = "Matthiola incana"
            elif flower_name == "scabiosa":
                korean_name = "스카비오사"
                scientific_name = "Scabiosa atropurpurea"
            elif flower_name == "dahlia":
                korean_name = "달리아"
                scientific_name = "Dahlia pinnata"
            elif flower_name == "rose":
                korean_name = "장미"
                scientific_name = "Rosa"
            elif flower_name == "lily":
                korean_name = "백합"
                scientific_name = "Lilium"
            elif flower_name == "tulip":
                korean_name = "튤립"
                scientific_name = "Tulipa"
            elif flower_name == "hydrangea":
                korean_name = "수국"
                scientific_name = "Hydrangea macrophylla"
            elif flower_name == "lisianthus":
                korean_name = "리시안서스"
                scientific_name = "Eustoma grandiflorum"
            elif flower_name == "bouvardia":
                korean_name = "부바르디아"
                scientific_name = "Bouvardia"
            elif flower_name == "freesia-refracta":
                korean_name = "프리지아"
                scientific_name = "Freesia Refracta"
            elif flower_name == "lathyrus-odoratus":
                korean_name = "스위트피"
                scientific_name = "Lathyrus Odoratus"
            elif flower_name == "ranunculus":
                korean_name = "라넌큘러스"
                scientific_name = "Ranunculus"
            elif flower_name == "gladiolus":
                korean_name = "글라디올러스"
                scientific_name = "Gladiolus"
            elif flower_name == "zinnia-elegans":
                korean_name = "백일홍"
                scientific_name = "Zinnia Elegans"
            
            # 기본 색상 설정
            default_color = colors[0] if colors else "화이트"
            
            # 키워드와 감정 설정 (기본값)
            keywords = ["아름다움", "자연스러움"]
            emotions = ["아름다움", "자연스러움"]
            
            # 특별한 경우 키워드 설정
            if "peony" in flower_name or "작약" in korean_name:
                keywords = ["우아함", "클래식", "세련됨", "추억", "그리움"]
                emotions = ["우아함", "클래식", "세련됨", "추억", "그리움"]
            elif "drumstick" in flower_name:
                keywords = ["독특함", "모던", "포인트", "재미"]
                emotions = ["재미", "독특함", "모던"]
            elif "cockscomb" in flower_name:
                keywords = ["독특함", "포인트", "화려함"]
                emotions = ["독특함", "화려함", "포인트"]
            elif "globe-amaranth" in flower_name:
                keywords = ["지속성", "내구성", "포인트"]
                emotions = ["지속성", "포인트", "내구성"]
            elif "babys-breath" in flower_name:
                keywords = ["부드러움", "우아함", "필러"]
                emotions = ["부드러움", "우아함", "순수"]
            elif "freesia-refracta" in flower_name:
                keywords = ["희망", "새로운 시작", "격려", "응원", "신뢰", "우정"]
                emotions = ["희망", "격려", "응원", "신뢰", "우정"]
            elif "gerbera-daisy" in flower_name:
                keywords = ["희망", "활력", "기쁨", "격려", "응원", "새로운 시작"]
                emotions = ["희망", "활력", "기쁨", "격려", "응원"]
            elif "tulip" in flower_name:
                keywords = ["희망", "새로운 시작", "완벽한 사랑", "기쁨", "활력"]
                emotions = ["희망", "완벽한 사랑", "기쁨", "활력"]
            elif "lathyrus-odoratus" in flower_name:
                keywords = ["우아한 추억", "나를 기억해 주세요", "즐거움", "떠나는 당신을 배웅하며", "달콤한 향기"]
                emotions = ["추억", "그리움", "사랑", "우정", "기억"]
            elif "ranunculus" in flower_name:
                keywords = ["우아함", "아름다움", "자연스러움", "순수함"]
                emotions = ["우아함", "아름다움", "순수함", "자연스러움"]
            elif "gladiolus" in flower_name:
                keywords = ["정렬적 사랑", "젊음", "향이 없음이 특징", "강렬함"]
                emotions = ["정렬적 사랑", "젊음", "강렬함", "열정"]
            elif "zinnia-elegans" in flower_name:
                keywords = ["인연", "그리움", "사랑하는 사람을 잊지 않겠다"]
                emotions = ["인연", "그리움", "사랑"]
            
            new_flower_database[display_name] = {
                "korean_name": korean_name,
                "scientific_name": scientific_name,
                "image_url": f'self.base64_images.get("{flower_name}", {{}}).get("{default_color}", "")',
                "keywords": keywords,
                "colors": colors,
                "emotions": emotions,
                "default_color": default_color
            }
        
        # flower_database 딕셔너리 교체
        import re
        
        # 기존 flower_database 찾기
        pattern = r'self\.flower_database = \{.*?\}'
        
        # 새로운 flower_database 문자열 생성
        new_db_str = "self.flower_database = {\n"
        for name, data in new_flower_database.items():
            new_db_str += f'            "{name}": {{\n'
            new_db_str += f'                "korean_name": "{data["korean_name"]}",\n'
            new_db_str += f'                "scientific_name": "{data["scientific_name"]}",\n'
            new_db_str += f'                "image_url": {data["image_url"]},\n'
            new_db_str += f'                "keywords": {data["keywords"]},\n'
            new_db_str += f'                "colors": {data["colors"]},\n'
            new_db_str += f'                "emotions": {data["emotions"]},\n'
            new_db_str += f'                "default_color": "{data["default_color"]}"\n'
            new_db_str += '            },\n'
        new_db_str += '        }'
        
        # 교체
        content = re.sub(pattern, new_db_str, content, flags=re.DOTALL)
        
        # _get_flower_folder 딕셔너리도 업데이트
        folder_pattern = r'_get_flower_folder = \{.*?\}'
        new_folder_str = "_get_flower_folder = {\n"
        for name in new_flower_database.keys():
            folder_name = name.lower().replace(' ', '-')
            new_folder_str += f'            "{name}": "{folder_name}",\n'
        new_folder_str += '        }'
        
        content = re.sub(folder_pattern, new_folder_str, content, flags=re.DOTALL)
        
        # 파일 저장
        with open(matcher_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ flower_matcher.py 완전 동기화 완료: {len(flowers)}개 꽃")
        
    except Exception as e:
        print(f"❌ flower_matcher.py 동기화 실패: {e}")
        raise e

async def update_base64_images():
    """base64_images.json 업데이트"""
    try:
        base64_file = "base64_images.json"
        base64_data = {}
        
        if os.path.exists(IMAGES_DIR):
            for folder in os.listdir(IMAGES_DIR):
                folder_path = os.path.join(IMAGES_DIR, folder)
                if os.path.isdir(folder_path):
                    folder_data = {}
                    image_files = [f for f in os.listdir(folder_path) if f.endswith('.webp')]
                    
                    for image_file in image_files:
                        color = image_file.replace('.webp', '')
                        image_path = os.path.join(folder_path, image_file)
                        
                        # 이미지를 base64로 인코딩
                        with open(image_path, "rb") as img_file:
                            img_data = img_file.read()
                            base64_string = base64.b64encode(img_data).decode('utf-8')
                            folder_data[color] = f"data:image/webp;base64,{base64_string}"
                    
                    if folder_data:
                        base64_data[folder] = folder_data
        
        # base64_images.json 저장
        with open(base64_file, 'w', encoding='utf-8') as f:
            json.dump(base64_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ base64_images.json 업데이트 완료: {len(base64_data)}개 폴더")
        
    except Exception as e:
        print(f"❌ base64_images.json 업데이트 실패: {e}")
        raise e
