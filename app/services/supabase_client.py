"""
Supabase 클라이언트 (읽기/쓰기 분리) + 스냅샷 저장 유틸
- READ: anon key (샘플/공개 데이터 조회)
- WRITE: service role key (RLS 우회하여 서버에서만 쓰기)
"""

from __future__ import annotations
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from postgrest.exceptions import APIError

# ──────────────────────────────────────────────────────────────
# 직렬화 유틸: Pydantic 모델/중첩 구조를 파이썬 기본형으로 변환
# ──────────────────────────────────────────────────────────────
def to_plain(obj):
    try:
        from pydantic import BaseModel
    except Exception:
        BaseModel = object  # pydantic 없는 환경 대비 (테스트)
    if isinstance(obj, BaseModel):
        # Pydantic v2
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        # v1 fallback
        if hasattr(obj, "dict"):
            return obj.dict()
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_plain(v) for v in obj]
    return obj  # str/int/float/bool/None


class SupabaseManager:
    """Supabase 읽기/쓰기 분리 매니저"""

    def __init__(self) -> None:
        url = os.getenv("SUPABASE_URL")
        anon = os.getenv("SUPABASE_ANON_KEY")
        service = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not url or not anon:
            raise ValueError("환경변수 SUPABASE_URL, SUPABASE_ANON_KEY가 필요합니다.")

        self.read: Client = create_client(url, anon)
        self.write: Optional[Client] = create_client(url, service) if service else None

        if not self.write:
            # 서버 콘솔에만 경고 남김(개발 중 눈에 띄게)
            print("⚠️  SUPABASE_SERVICE_ROLE_KEY 미설정 - 서버에서 쓰기 작업(insert/update)이 실패할 수 있어요.")

    # ── 샘플 스토리: 조회 전용 (anon) ─────────────────────────
    def get_all_stories(self) -> List[Dict[str, Any]]:
        try:
            resp = self.read.table("sample_stories").select("*").order("id").execute()
            return resp.data or []
        except Exception as e:
            print(f"❌ 샘플 스토리 조회 실패: {e}")
            return []

    def get_story_by_id(self, story_id: str) -> Optional[Dict[str, Any]]:
        try:
            resp = self.read.table("sample_stories").select("*").eq("id", story_id).single().execute()
            return resp.data
        except Exception as e:
            print(f"❌ 스토리 조회 실패({story_id}): {e}")
            return None

    def get_stories_by_category(self, category: str) -> List[Dict[str, Any]]:
        try:
            resp = self.read.table("sample_stories").select("*").eq("category", category).order("id").execute()
            return resp.data or []
        except Exception as e:
            print(f"❌ 카테고리별 스토리 조회 실패({category}): {e}")
            return []

    def get_categories(self) -> List[str]:
        try:
            resp = self.read.table("sample_stories").select("category").execute()
            cats = {row["category"] for row in (resp.data or []) if "category" in row}
            return sorted(cats)
        except Exception as e:
            print(f"❌ 카테고리 조회 실패: {e}")
            return []

    def get_total_count(self) -> int:
        try:
            resp = self.read.table("sample_stories").select("id", count="exact").execute()
            return int(getattr(resp, "count", 0) or 0)
        except Exception as e:
            print(f"❌ 총 개수 조회 실패: {e}")
            return 0

    # ── 추천 스냅샷: 쓰기 (service) & 조회(anon) ──────────────
    def _next_story_id(self, flower_code: str, yymmdd: str | None = None) -> str:
        """DB 기준으로 마지막 id를 찾아 +1"""
        yymmdd = yymmdd or datetime.now().strftime("%y%m%d")
        prefix = f"S{yymmdd}-{flower_code}-"

        resp = (
            self.read.table("recommendation_snapshots")
            .select("id")
            .like("id", f"{prefix}%")
            .order("id", desc=True)
            .limit(1)
            .execute()
        )

        if resp.data:
            last = resp.data[0]["id"]                       # ex) S250929-DEF-000123
            last_seq = int(last.rsplit("-", 1)[1])
            seq = last_seq + 1
        else:
            seq = 1

        return f"{prefix}{seq:06d}"

    def insert_snapshot_autoinc(self, snapshot_data: dict, flower_code: str, max_retries: int = 5):
        """
        DB에서 마지막 번호 +1로 story_id 생성 후 insert.
        드물게 23505(중복키) 뜨면 재시도.
        """
        if not self.write:
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY가 없어 write를 사용할 수 없습니다.")

        for attempt in range(max_retries):
            story_id = self._next_story_id(flower_code)
            payload = to_plain(snapshot_data)  # JSON 직렬화를 위해 to_plain 적용
            payload["id"] = story_id

            try:
                resp = self.write.table("recommendation_snapshots").insert(payload).execute()
                if getattr(resp, "error", None):
                    # supabase-py v2 응답 에러 형식 방어
                    raise APIError(resp.error)
                data = getattr(resp, "data", None)
                if data:
                    print(f"✅ 저장 성공: {story_id}")
                    return data[0] if isinstance(data, list) else data
                print("❌ Supabase 응답에 data 없음:", resp)
                return None

            except APIError as e:
                # postgrest APIError는 dict가 args[0]에 있음
                code = None
                try:
                    code = (e.args[0] or {}).get("code")
                except Exception:
                    pass

                if code == "23505":
                    # 중복 키 → 다른 번호로 다시 시도
                    print(f"⚠️ 중복 충돌(23505) 재시도 {attempt+1}/{max_retries}")
                    continue
                # 다른 에러는 바로 종료
                print("❌ APIError:", e.args[0] if e.args else str(e))
                return None

            except Exception as e:
                print("❌ 예외:", type(e), str(e))
                return None

        print("❌ 최대 재시도 초과로 저장 실패")
        return None

    def insert_recommendation_snapshot(self, snapshot_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """RLS가 켜진 테이블에 서버에서 안전하게 INSERT (service role key 필요)"""
        try:
            if not self.write:
                raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY가 없어 write 클라이언트를 사용할 수 없습니다.")

            payload = to_plain(snapshot_data)
            print("🔍 Supabase 저장 시도(service):", payload)

            # created_at은 DB default(now()) 권장 (스키마에 DEFAULT now() 설정)
            resp = self.write.table("recommendation_snapshots").insert(payload).execute()

            if getattr(resp, "error", None):
                print("❌ Supabase error:", resp.error)
                return None

            data = getattr(resp, "data", None)
            if data:
                print("✅ Supabase 저장 성공:", data)
                return data[0] if isinstance(data, list) else data

            print("❌ Supabase 응답에 data 없음:", resp)
            return None
        except Exception as e:
            import traceback
            print("❌ 스냅샷 저장 실패:", e)
            print("❌ 오류 타입:", type(e))
            print("❌ 오류 상세:", str(e))
            print("❌ Trace:\n", traceback.format_exc())
            return None

    def get_recommendation_snapshot(self, story_id: str) -> Optional[Dict[str, Any]]:
        try:
            resp = self.read.table("recommendation_snapshots").select("*").eq("id", story_id).single().execute()
            return resp.data
        except Exception as e:
            print(f"❌ 스냅샷 조회 실패({story_id}): {e}")
            return None

    def get_recommendation_snapshots_by_flower(self, flower_name: str) -> List[Dict[str, Any]]:
        try:
            resp = (
                self.read.table("recommendation_snapshots")
                .select("*")
                .eq("flower_name", flower_name)
                .order("created_at", desc=True)
                .execute()
            )
            return resp.data or []
        except Exception as e:
            print(f"❌ 꽃별 스냅샷 조회 실패({flower_name}): {e}")
            return []

    def get_recent_snapshots(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            resp = (
                self.read.table("recommendation_snapshots")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return resp.data or []
        except Exception as e:
            print("❌ 최근 스냅샷 조회 실패:", e)
            return []


# ── 싱글톤 ───────────────────────────────────────────────────
_manager: Optional[SupabaseManager] = None

def get_supabase_manager() -> SupabaseManager:
    global _manager
    if _manager is None:
        _manager = SupabaseManager()
    return _manager