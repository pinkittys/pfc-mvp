from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any

from app.models.schemas import (
    StoryCreateRequest, StoryResponse, StoryShareRequest, 
    StoryShareResponse, StoryData
)
from app.services.story_manager import story_manager

router = APIRouter()


@router.post("/create", response_model=StoryResponse)
async def create_story(request: StoryCreateRequest):
    """새로운 스토리 생성"""
    try:
        story_data = story_manager.create_story(request)
        return StoryResponse(
            success=True,
            message="스토리가 성공적으로 생성되었습니다.",
            data=story_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스토리 생성 중 오류가 발생했습니다: {str(e)}")


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str):
    """스토리 ID로 스토리 조회"""
    story_data = story_manager.get_story(story_id)
    if not story_data:
        raise HTTPException(status_code=404, detail="스토리를 찾을 수 없습니다.")
    
    return StoryResponse(
        success=True,
        message="스토리를 성공적으로 조회했습니다.",
        data=story_data
    )


@router.post("/share", response_model=StoryShareResponse)
async def share_story(request: StoryShareRequest):
    """스토리 공유 URL 생성"""
    story_data = story_manager.get_story(request.story_id)
    if not story_data:
        raise HTTPException(status_code=404, detail="스토리를 찾을 수 없습니다.")
    
    # 공유 URL 생성 (Base64 인코딩된 스토리 ID)
    import base64
    encoded_id = base64.urlsafe_b64encode(request.story_id.encode()).decode()
    share_url = f"/share/{encoded_id}"
    
    return StoryShareResponse(
        success=True,
        message="공유 URL이 생성되었습니다.",
        data=story_data,
        share_url=share_url
    )


@router.get("/share/{encoded_id}", response_model=StoryResponse)
async def get_shared_story(encoded_id: str):
    """공유된 스토리 조회"""
    try:
        import base64
        story_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
        story_data = story_manager.get_story(story_id)
        
        if not story_data:
            raise HTTPException(status_code=404, detail="공유된 스토리를 찾을 수 없습니다.")
        
        return StoryResponse(
            success=True,
            message="공유된 스토리를 성공적으로 조회했습니다.",
            data=story_data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="잘못된 공유 URL입니다.")


@router.put("/{story_id}", response_model=StoryResponse)
async def update_story(story_id: str, update_data: Dict[str, Any]):
    """스토리 업데이트"""
    story_data = story_manager.update_story(story_id, update_data)
    if not story_data:
        raise HTTPException(status_code=404, detail="스토리를 찾을 수 없습니다.")
    
    return StoryResponse(
        success=True,
        message="스토리가 성공적으로 업데이트되었습니다.",
        data=story_data
    )


@router.delete("/{story_id}")
async def delete_story(story_id: str):
    """스토리 삭제"""
    success = story_manager.delete_story(story_id)
    if not success:
        raise HTTPException(status_code=404, detail="스토리를 찾을 수 없습니다.")
    
    return {"success": True, "message": "스토리가 성공적으로 삭제되었습니다."}


@router.get("/stats/count")
async def get_story_count():
    """전체 스토리 개수 조회"""
    count = story_manager.get_story_count()
    return {"total_count": count}


@router.get("/stats/daily/{date_str}")
async def get_daily_story_count(date_str: str):
    """특정 날짜의 스토리 개수 조회"""
    count = story_manager.get_daily_story_count(date_str)
    return {"date": date_str, "count": count}


@router.get("/list/all")
async def get_all_stories():
    """모든 스토리 목록 조회 (관리자용)"""
    stories = story_manager.get_all_stories()
    return {
        "success": True,
        "total_count": len(stories),
        "stories": {story_id: story.dict() for story_id, story in stories.items()}
    }


@router.get("/list/by-date/{date_str}")
async def get_stories_by_date(date_str: str):
    """특정 날짜의 스토리 목록 조회"""
    stories = story_manager.get_stories_by_date(date_str)
    return {
        "success": True,
        "date": date_str,
        "count": len(stories),
        "stories": {story_id: story.dict() for story_id, story in stories.items()}
    }


@router.get("/list/by-flower/{flower_name}")
async def get_stories_by_flower(flower_name: str):
    """특정 꽃에 대한 스토리 목록 조회"""
    stories = story_manager.get_stories_by_flower(flower_name)
    return {
        "success": True,
        "flower_name": flower_name,
        "count": len(stories),
        "stories": {story_id: story.dict() for story_id, story in stories.items()}
    }
