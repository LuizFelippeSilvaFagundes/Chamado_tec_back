"""
Controller para gerenciamento de anexos de tickets
"""
from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.models import Ticket
import os
import shutil
from pathlib import Path
from uuid import uuid4
from typing import List


# Diretório para salvar anexos
ATTACHMENT_DIR = Path("static/attachments")
ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)

# Extensões permitidas
ALLOWED_EXTENSIONS = {
    # Imagens
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    # Documentos
    ".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx",
    # Outros
    ".zip", ".rar"
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def upload_ticket_attachments(ticket_id: int, files: List[UploadFile], db: Session, user_id: int):
    """
    Upload de anexos para um ticket
    """
    # Buscar ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    # Verificar permissão: usuário dono do ticket ou técnico atribuído
    if ticket.user_id != user_id and ticket.assigned_technician_id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão para adicionar anexos neste ticket")
    
    # Lista atual de anexos
    current_attachments = ticket.attachments or []
    
    uploaded_files = []
    
    for file in files:
        # Validar extensão
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Extensão não permitida: {file_ext}. Use: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Validar tamanho
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo {file.filename} muito grande. Máximo: 10MB"
            )
        
        # Gerar nome único
        unique_filename = f"{uuid4()}{file_ext}"
        file_path = ATTACHMENT_DIR / unique_filename
        
        # Salvar arquivo
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
        
        # Adicionar à lista de anexos
        attachment_info = {
            "filename": file.filename,
            "stored_filename": unique_filename,
            "url": f"/static/attachments/{unique_filename}",
            "size": file.size or 0,
            "type": file.content_type or "application/octet-stream"
        }
        current_attachments.append(attachment_info)
        uploaded_files.append(attachment_info)
    
    # Atualizar ticket
    ticket.attachments = current_attachments
    db.commit()
    db.refresh(ticket)
    
    return {
        "message": f"{len(uploaded_files)} arquivo(s) enviado(s) com sucesso",
        "uploaded_files": uploaded_files,
        "total_attachments": len(current_attachments)
    }


def get_ticket_attachments(ticket_id: int, db: Session):
    """
    Obter lista de anexos de um ticket
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    return {
        "ticket_id": ticket_id,
        "attachments": ticket.attachments or [],
        "total": len(ticket.attachments or [])
    }


def download_attachment(ticket_id: int, filename: str, db: Session):
    """
    Download de um anexo específico
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    if not ticket.attachments:
        raise HTTPException(status_code=404, detail="Ticket não possui anexos")
    
    # Procurar anexo
    attachment = None
    for att in ticket.attachments:
        if att.get("stored_filename") == filename:
            attachment = att
            break
    
    if not attachment:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")
    
    file_path = ATTACHMENT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no servidor")
    
    return FileResponse(
        path=file_path,
        filename=attachment["filename"],
        media_type=attachment.get("type", "application/octet-stream")
    )


def delete_attachment(ticket_id: int, filename: str, db: Session, user_id: int):
    """
    Deletar um anexo de um ticket
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    # Verificar permissão
    if ticket.user_id != user_id and ticket.assigned_technician_id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão para deletar anexos deste ticket")
    
    if not ticket.attachments:
        raise HTTPException(status_code=404, detail="Ticket não possui anexos")
    
    # Procurar e remover anexo
    attachment_to_remove = None
    new_attachments = []
    
    for att in ticket.attachments:
        if att.get("stored_filename") == filename:
            attachment_to_remove = att
        else:
            new_attachments.append(att)
    
    if not attachment_to_remove:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")
    
    # Deletar arquivo físico
    file_path = ATTACHMENT_DIR / filename
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"Erro ao deletar arquivo: {e}")
    
    # Atualizar ticket
    ticket.attachments = new_attachments if new_attachments else None
    db.commit()
    db.refresh(ticket)
    
    return {
        "message": "Anexo deletado com sucesso",
        "deleted_file": attachment_to_remove["filename"],
        "remaining_attachments": len(new_attachments)
    }

