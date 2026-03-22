"""
交付物服务
处理文件上传、下载和管理业务逻辑
"""

import os
import hashlib
import shutil
from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile

from sqlalchemy.orm import Session
from ..models.deliverable import Deliverable, DeliverableStatus, FileType
from ..models.checklist import ChecklistItem
from .. import config


class DeliverableService:
    """交付物服务类"""
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {
        '.pdf': FileType.PDF,
        '.doc': FileType.WORD,
        '.docx': FileType.WORD,
        '.xls': FileType.EXCEL,
        '.xlsx': FileType.EXCEL,
        '.txt': FileType.OTHER,
        '.sh': FileType.SCRIPT,
        '.py': FileType.SCRIPT,
        '.log': FileType.LOG,
    }
    
    # 文件大小限制 (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, deliverable_id: int) -> Optional[Deliverable]:
        """根据ID获取交付物"""
        return self.db.query(Deliverable).filter(
            Deliverable.id == deliverable_id,
            Deliverable.status == DeliverableStatus.ACTIVE
        ).first()
    
    def get_by_checklist_item(self, checklist_item_id: int) -> List[Deliverable]:
        """获取检查项的所有交付物"""
        return self.db.query(Deliverable).filter(
            Deliverable.checklist_item_id == checklist_item_id,
            Deliverable.status == DeliverableStatus.ACTIVE
        ).order_by(Deliverable.uploaded_at.desc()).all()
    
    def get_by_task(self, task_id: int) -> List[Deliverable]:
        """获取任务的所有交付物"""
        from ..models.checklist import ChecklistItem
        
        return self.db.query(Deliverable).join(
            ChecklistItem,
            Deliverable.checklist_item_id == ChecklistItem.id
        ).filter(
            ChecklistItem.task_id == task_id,
            Deliverable.status == DeliverableStatus.ACTIVE
        ).order_by(Deliverable.uploaded_at.desc()).all()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Deliverable]:
        """获取所有交付物"""
        return self.db.query(Deliverable).filter(
            Deliverable.status == DeliverableStatus.ACTIVE
        ).order_by(Deliverable.uploaded_at.desc()).offset(skip).limit(limit).all()
    
    def _get_file_type(self, filename: str) -> FileType:
        """根据文件名获取文件类型"""
        ext = os.path.splitext(filename.lower())[1]
        return self.ALLOWED_EXTENSIONS.get(ext, FileType.OTHER)
    
    def _validate_file(self, file: UploadFile) -> None:
        """验证文件"""
        # 检查文件扩展名
        ext = os.path.splitext(file.filename.lower())[1]
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"不支持的文件类型: {ext}。支持的类型: {', '.join(self.ALLOWED_EXTENSIONS.keys())}")
        
        # 检查文件大小（这里只是初步检查，实际大小在保存时确定）
        # 实际文件大小检查在保存后进行
    
    def _save_file(self, file: UploadFile) -> tuple:
        """
        保存文件到磁盘
        返回: (文件路径, 文件大小, 文件Hash)
        """
        # 创建上传目录
        today = datetime.now()
        upload_dir = os.path.join(
            str(config.UPLOAD_DIR),
            str(today.year),
            f"{today.month:02d}",
            f"{today.day:02d}"
        )
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成文件Hash作为文件名
        content = file.file.read()
        file_hash = hashlib.md5(content).hexdigest()
        
        # 获取文件扩展名
        ext = os.path.splitext(file.filename.lower())[1]
        new_filename = f"{file_hash}{ext}"
        file_path = os.path.join(upload_dir, new_filename)
        
        # 检查文件大小
        file_size = len(content)
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"文件大小超过限制: {file_size / 1024 / 1024:.2f}MB > {self.MAX_FILE_SIZE / 1024 / 1024}MB")
        
        # 如果文件已存在，直接返回（去重）
        if os.path.exists(file_path):
            return file_path, file_size, file_hash
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(content)
        
        return file_path, file_size, file_hash
    
    def upload_file(
        self,
        checklist_item_id: int,
        file: UploadFile,
        description: Optional[str],
        uploader_id: int
    ) -> Deliverable:
        """
        上传文件
        """
        # 验证检查项是否存在
        checklist_item = self.db.query(ChecklistItem).filter(
            ChecklistItem.id == checklist_item_id
        ).first()
        if not checklist_item:
            raise ValueError("检查项不存在")
        
        # 验证文件
        self._validate_file(file)
        
        # 保存文件
        file_path, file_size, file_hash = self._save_file(file)
        
        # 创建数据库记录
        deliverable = Deliverable(
            checklist_item_id=checklist_item_id,
            uploader_id=uploader_id,
            file_name=file.filename,
            file_type=self._get_file_type(file.filename),
            file_size=file_size,
            file_path=file_path,
            file_hash=file_hash,
            description=description,
            status=DeliverableStatus.ACTIVE
        )
        
        self.db.add(deliverable)
        
        # 更新检查项的交付物数量
        checklist_item.deliverable_count = self.db.query(Deliverable).filter(
            Deliverable.checklist_item_id == checklist_item_id,
            Deliverable.status == DeliverableStatus.ACTIVE
        ).count() + 1
        
        self.db.commit()
        self.db.refresh(deliverable)
        
        return deliverable
    
    def delete_deliverable(self, deliverable_id: int, user_id: int) -> None:
        """
        删除交付物（软删除）
        """
        deliverable = self.get_by_id(deliverable_id)
        if not deliverable:
            raise ValueError("交付物不存在")
        
        # 检查权限（仅上传者或管理员可删除）
        # TODO: 添加管理员角色检查
        if deliverable.uploader_id != user_id:
            raise ValueError("无权删除此文件")
        
        # 软删除
        deliverable.status = DeliverableStatus.DELETED
        
        # 更新检查项的交付物数量
        checklist_item = self.db.query(ChecklistItem).filter(
            ChecklistItem.id == deliverable.checklist_item_id
        ).first()
        if checklist_item:
            checklist_item.deliverable_count = self.db.query(Deliverable).filter(
                Deliverable.checklist_item_id == deliverable.checklist_item_id,
                Deliverable.status == DeliverableStatus.ACTIVE
            ).count()
        
        self.db.commit()
