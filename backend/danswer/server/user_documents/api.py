from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from danswer.auth.users import current_user
from danswer.db.engine import get_session
from danswer.db.models import User
from danswer.db.models import UserFile
from danswer.db.models import UserFolder
from danswer.server.documents.connector import upload_files
from danswer.server.documents.models import FileUploadResponse
from danswer.server.user_documents.models import FileResponse
from danswer.server.user_documents.models import FileSystemResponse
from danswer.server.user_documents.models import FolderDetailResponse
from danswer.server.user_documents.models import FolderFullDetailResponse
from danswer.server.user_documents.models import FolderResponse
from danswer.server.user_documents.models import MessageResponse

router = APIRouter()


class FolderCreationRequest(BaseModel):
    name: str
    parent_id: int | None = None


@router.post("/user/folder")
def create_folder(
    request: FolderCreationRequest,
    user: User = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> FolderDetailResponse:
    new_folder = UserFolder(
        user_id=user.id if user else None,
        parent_id=None if request.parent_id == -1 else request.parent_id,
        name=request.name,
    )
    db_session.add(new_folder)
    db_session.commit()
    return FolderDetailResponse(
        id=new_folder.id,
        name=new_folder.name,
        parent_id=new_folder.parent_id,
        children=[],
        files=[],
    )


@router.get(
    "/user/folder",
)
def get_folders(
    user: User = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> List[FolderResponse]:
    user_id = user.id if user else None
    folders = db_session.query(UserFolder).filter(UserFolder.user_id == user_id).all()
    return [FolderResponse.from_model(folder) for folder in folders]


@router.get("/user/folder/{folder_id}")
def get_folder(
    folder_id: int,
    user: User | None = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> FolderFullDetailResponse:
    user_id = user.id if user else None
    if folder_id == -1:
        children = (
            db_session.query(UserFolder)
            .filter(UserFolder.user_id == user_id, UserFolder.parent_id.is_(None))
            .all()
        )
        files = (
            db_session.query(UserFile)
            .filter(UserFile.user_id == user_id, UserFile.parent_folder_id.is_(None))
            .all()
        )
        return FolderFullDetailResponse(
            name="Default Folder",
            parent_id=None,
            id=-1,
            children=[FolderResponse.from_model(child).dict() for child in children],
            files=[FileResponse.from_model(file).dict() for file in files],
            parents=[],
        )
    else:
        folder = (
            db_session.query(UserFolder)
            .filter(UserFolder.id == folder_id, UserFolder.user_id == user_id)
            .first()
        )
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")

        parents: List[FolderResponse] = []
        current_folder = folder
        while current_folder.parent_id is not None:
            parent = (
                db_session.query(UserFolder)
                .filter(UserFolder.id == current_folder.parent_id)
                .first()
            )
            if parent:
                parents.insert(
                    0,
                    FolderResponse.from_model(parent).dict(),
                )
                current_folder = parent
            else:
                break
        return FolderFullDetailResponse(
            name=folder.name,
            parent_id=folder.parent_id,
            id=folder.id,
            children=[
                FolderResponse.from_model(child).dict() for child in folder.children
            ],
            files=[FileResponse.from_model(file).dict() for file in folder.files],
            parents=parents,
        )


@router.post("/user/file/upload")
def upload_user_files(
    files: List[UploadFile] = File(...),
    folder_id: int | None = Form(None),
    user: User = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> FileUploadResponse:
    upload_response = upload_files(files, db_session)
    for file_path, file in zip(upload_response.file_paths, files):
        new_file = UserFile(
            user_id=user.id if user else None,
            parent_folder_id=folder_id,
            file_id=file_path,
            document_id=file_path,  # We'll use the same ID for now
            name=file.filename,
        )
        db_session.add(new_file)

    db_session.commit()
    return upload_response


@router.put("/user/folder/{folder_id}")
def update_folder(
    folder_id: int,
    name: str,
    user: User | None = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> FolderDetailResponse:
    user_id = user.id if user else None
    folder = (
        db_session.query(UserFolder)
        .filter(UserFolder.id == folder_id, UserFolder.user_id == user_id)
        .first()
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    folder.name = name
    db_session.commit()
    return FolderDetailResponse(
        id=folder.id,
        name=folder.name,
        parent_id=folder.parent_id,
        children=[FolderResponse.from_model(child) for child in folder.children],
        files=[FileResponse.from_model(file) for file in folder.files],
    )


@router.delete("/user/folder/{folder_id}")
def delete_folder(
    folder_id: int,
    user: User = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> MessageResponse:
    user_id = user.id if user else None
    folder = (
        db_session.query(UserFolder)
        .filter(UserFolder.id == folder_id, UserFolder.user_id == user_id)
        .first()
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    db_session.delete(folder)
    db_session.commit()
    return MessageResponse(message="Folder deleted successfully")


@router.put("/user/folder/{folder_id}/move")
def move_folder(
    folder_id: int,
    new_parent_id: int | None,
    user: User = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> FolderResponse:
    user_id = user.id if user else None
    folder = (
        db_session.query(UserFolder)
        .filter(UserFolder.id == folder_id, UserFolder.user_id == user_id)
        .first()
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    folder.parent_id = new_parent_id
    db_session.commit()
    return FolderResponse.from_model(folder)


@router.delete("/user/file/{file_id}")
def delete_file(
    file_id: int,
    user: User = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> MessageResponse:
    user_id = user.id if user else None
    file = (
        db_session.query(UserFile)
        .filter(UserFile.id == file_id, UserFile.user_id == user_id)
        .first()
    )
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    db_session.delete(file)
    db_session.commit()
    return MessageResponse(message="File deleted successfully")


@router.put("/user/file/{file_id}/move")
def move_file(
    file_id: int,
    new_folder_id: int | None,
    user: User = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> FileResponse:
    user_id = user.id if user else None
    file = (
        db_session.query(UserFile)
        .filter(UserFile.id == file_id, UserFile.user_id == user_id)
        .first()
    )
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    file.parent_folder_id = new_folder_id
    db_session.commit()
    return FileResponse.from_model(file)


@router.get("/user/file-system")
def get_file_system(
    user: User = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> FileSystemResponse:
    user_id = user.id if user else None
    folders = db_session.query(UserFolder).filter(UserFolder.user_id == user_id).all()
    files = db_session.query(UserFile).filter(UserFile.user_id == user_id).all()
    return FileSystemResponse(
        folders=[FolderResponse.from_model(folder) for folder in folders],
        files=[FileResponse.from_model(file) for file in files],
    )