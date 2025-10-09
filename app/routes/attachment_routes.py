"""
Rotas para gerenciamento de anexos de tickets
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.controllers import attachment_controller
from app.models import User
from typing import List

router = APIRouter(prefix="/tickets/{ticket_id}/attachments", tags=["Ticket Attachments"])


@router.post("/upload")
async def upload_attachments(
    ticket_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload de anexos para um ticket
    
    - **ticket_id**: ID do ticket
    - **files**: Lista de arquivos (imagens, PDFs, documentos)
    - Tamanho máximo por arquivo: 10MB
    """
    return attachment_controller.upload_ticket_attachments(
        ticket_id, files, db, current_user.id
    )


@router.get("/")
async def get_attachments(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """
    Listar anexos de um ticket
    """
    return attachment_controller.get_ticket_attachments(ticket_id, db)


@router.get("/download/{filename}")
async def download_attachment(
    ticket_id: int,
    filename: str,
    db: Session = Depends(get_db)
):
    """
    Download de um anexo específico
    
    - **ticket_id**: ID do ticket
    - **filename**: Nome do arquivo armazenado
    """
    return attachment_controller.download_attachment(ticket_id, filename, db)


@router.delete("/{filename}")
async def delete_attachment(
    ticket_id: int,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletar um anexo de um ticket
    
    - Apenas o dono do ticket ou técnico atribuído podem deletar
    """
    return attachment_controller.delete_attachment(
        ticket_id, filename, db, current_user.id
    )

