from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from typing import Any

from app.db.session import get_db
from app.models.user import User
from app.models.saved_search import SavedSearch
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/saved-searches", tags=["saved-searches"])


# --- Schémas Pydantic ---

class SavedSearchCreate(BaseModel):
    name: str
    query_json: Any  # Structure JSON libre (query, filters, logical_query, etc.)


class SavedSearchResponse(BaseModel):
    id: int
    name: str
    query_json: Any
    created_at: str

    class Config:
        from_attributes = True


# --- Endpoints ---

@router.get("", response_model=List[SavedSearchResponse])
def list_saved_searches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retourne toutes les recherches sauvegardées de l'utilisateur connecté."""
    searches = (
        db.query(SavedSearch)
        .filter(SavedSearch.user_id == current_user.id)
        .order_by(SavedSearch.created_at.desc())
        .all()
    )
    return [
        SavedSearchResponse(
            id=s.id,
            name=s.name,
            query_json=s.query_json,
            created_at=s.created_at.isoformat(),
        )
        for s in searches
    ]


@router.post("", response_model=SavedSearchResponse, status_code=status.HTTP_201_CREATED)
def create_saved_search(
    payload: SavedSearchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sauvegarde une nouvelle recherche pour l'utilisateur connecté."""
    if not payload.name or not payload.name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Search name cannot be empty",
        )
    if payload.query_json is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="query_json cannot be null",
        )

    saved = SavedSearch(
        user_id=current_user.id,
        name=payload.name.strip(),
        query_json=payload.query_json,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)

    return SavedSearchResponse(
        id=saved.id,
        name=saved.name,
        query_json=saved.query_json,
        created_at=saved.created_at.isoformat(),
    )


@router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Supprime une recherche sauvegardée (appartenant à l'utilisateur connecté)."""
    saved = (
        db.query(SavedSearch)
        .filter(SavedSearch.id == search_id, SavedSearch.user_id == current_user.id)
        .first()
    )
    if not saved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found",
        )
    db.delete(saved)
    db.commit()
