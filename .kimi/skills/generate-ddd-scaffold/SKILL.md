# Skill: generate-ddd-scaffold

## 基本信息

- **名称**: generate-ddd-scaffold
- **描述**: 根据 PRD 自动生成 DDD 分层架构的代码骨架
- **调用方式**: `/skill:generate-ddd-scaffold --prd=<PRD文件名>`

## 使用场景

编写完 PRD 后，需要快速生成后端代码模板，包括：
1. DDD 分层目录结构
2. 领域实体和值对象
3. 仓储接口和实现
4. 应用服务和 DTO
5. API 路由和 Schema

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--prd` | string | 是 | PRD 文件名（如 `Module_04_Verification_Execution.md`） |
| `--module-name` | string | 否 | 模块名称（默认从 PRD 文件名解析） |
| `--with-tests` | flag | 否 | 同时生成测试代码骨架 |

## 执行步骤

### 1. 解析 PRD

读取 `OpsPilot_AI_PRD_Docs/Modules/{prd}`，提取：
- 模块名称和职责
- 领域实体定义（属性、方法、关系）
- 值对象定义
- 接口定义（REST API）
- 跨模块依赖关系

### 2. 生成 DDD 目录结构

```
backend/app/modules/{module_name}/
├── __init__.py                    # 模块组装和导出
├── domain/
│   ├── __init__.py
│   ├── entities/
│   │   ├── __init__.py
│   │   └── {entity_name}.py       # 领域实体
│   ├── value_objects/
│   │   ├── __init__.py
│   │   └── {vo_name}.py           # 值对象
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── {entity}_repository.py # 仓储接口
│   ├── services/
│   │   └── __init__.py
│   └── events/
│       ├── __init__.py
│       └── {module}_events.py     # 领域事件
├── application/
│   ├── __init__.py
│   ├── dtos/
│   │   ├── __init__.py
│   │   └── {module}_dtos.py       # DTO 定义
│   └── {module}_service.py        # 应用服务
├── infrastructure/
│   ├── __init__.py
│   └── persistence/
│       ├── __init__.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── {entity}_model.py  # SQLAlchemy 模型
│       └── repositories/
│           ├── __init__.py
│           └── {entity}_repository_impl.py
└── interfaces/
    ├── __init__.py
    └── api/
        ├── __init__.py
        ├── routes/
        │   ├── __init__.py
        │   └── {module}_routes.py # FastAPI 路由
        └── schemas/
            ├── __init__.py
            └── {module}_schemas.py # Pydantic Schema
```

### 3. 生成领域层代码

**实体模板**:
```python
# domain/entities/{entity}.py
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

from app.modules.{module}.domain.value_objects.{status_vo} import {Status}VO


@dataclass
class {Entity}:
    """{实体描述}"""
    id: Optional[int] = None
    name: str = ""
    status: {Status}VO = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def create(cls, name: str, ...) -> "{Entity}":
        """创建新实体"""
        return cls(
            name=name,
            status={Status}VO.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    def update(self, **kwargs):
        """更新实体"""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
```

**值对象模板**:
```python
# domain/value_objects/{vo_name}.py
from enum import Enum


class {Status}VO(str, Enum):
    """{状态描述}"""
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

**仓储接口模板**:
```python
# domain/repositories/{entity}_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.{module}.domain.entities.{entity} import {Entity}


class I{Entity}Repository(ABC):
    """{实体}仓储接口"""

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[{Entity}]:
        """根据 ID 获取"""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[{Entity}]:
        """获取列表"""
        pass

    @abstractmethod
    def create(self, entity: {Entity}) -> {Entity}:
        """创建"""
        pass

    @abstractmethod
    def update(self, entity: {Entity}) -> {Entity}:
        """更新"""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """删除"""
        pass
```

### 4. 生成应用层代码

**DTO 模板**:
```python
# application/dtos/{module}_dtos.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Create{Entity}DTO(BaseModel):
    """创建{实体}请求"""
    name: str
    description: Optional[str] = None


class Update{Entity}DTO(BaseModel):
    """更新{实体}请求"""
    name: Optional[str] = None
    description: Optional[str] = None


class {Entity}ResponseDTO(BaseModel):
    """{实体}响应"""
    id: int
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
```

**应用服务模板**:
```python
# application/{module}_service.py
from typing import List, Optional

from app.modules.{module}.domain.entities.{entity} import {Entity}
from app.modules.{module}.domain.repositories.{entity}_repository import I{Entity}Repository
from app.modules.{module}.application.dtos.{module}_dtos import (
    Create{Entity}DTO,
    Update{Entity}DTO,
    {Entity}ResponseDTO
)


class {Module}Service:
    """{模块}应用服务"""

    def __init__(self, {entity}_repo: I{Entity}Repository):
        self._{entity}_repo = {entity}_repo

    def create_{entity}(self, dto: Create{Entity}DTO) -> {Entity}ResponseDTO:
        """创建{实体}"""
        entity = {Entity}.create(name=dto.name, description=dto.description)
        saved = self._{entity}_repo.create(entity)
        return {Entity}ResponseDTO(**saved.to_dict())

    def get_{entity}(self, id: int) -> Optional[{Entity}ResponseDTO]:
        """获取{实体}"""
        entity = self._{entity}_repo.get_by_id(id)
        if entity:
            return {Entity}ResponseDTO(**entity.to_dict())
        return None

    def list_{entity}s(self, skip: int = 0, limit: int = 100) -> List[{Entity}ResponseDTO]:
        """获取{实体}列表"""
        entities = self._{entity}_repo.get_all(skip=skip, limit=limit)
        return [{Entity}ResponseDTO(**e.to_dict()) for e in entities]

    def update_{entity}(self, id: int, dto: Update{Entity}DTO) -> Optional[{Entity}ResponseDTO]:
        """更新{实体}"""
        entity = self._{entity}_repo.get_by_id(id)
        if not entity:
            return None
        entity.update(**dto.dict(exclude_unset=True))
        updated = self._{entity}_repo.update(entity)
        return {Entity}ResponseDTO(**updated.to_dict())

    def delete_{entity}(self, id: int) -> bool:
        """删除{实体}"""
        return self._{entity}_repo.delete(id)
```

### 5. 生成基础设施层代码

**SQLAlchemy 模型模板**:
```python
# infrastructure/persistence/models/{entity}_model.py
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func

from app.core.database import Base


class {Entity}Model(Base):
    """{实体}数据库模型"""
    __tablename__ = "{module}_{entity}s"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_entity(self) -> "{Entity}":
        """转换为领域实体"""
        from app.modules.{module}.domain.entities.{entity} import {Entity}
        return {Entity}(
            id=self.id,
            name=self.name,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_entity(cls, entity: "{Entity}") -> "{Entity}Model":
        """从领域实体创建"""
        return cls(
            id=entity.id,
            name=entity.name,
            status=entity.status.value if entity.status else "draft"
        )
```

**仓储实现模板**:
```python
# infrastructure/persistence/repositories/{entity}_repository_impl.py
from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.{module}.domain.entities.{entity} import {Entity}
from app.modules.{module}.domain.repositories.{entity}_repository import I{Entity}Repository
from app.modules.{module}.infrastructure.persistence.models.{entity}_model import {Entity}Model


class {Entity}RepositoryImpl(I{Entity}Repository):
    """{实体}仓储实现"""

    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, id: int) -> Optional[{Entity}]:
        model = self._db.query({Entity}Model).filter({Entity}Model.id == id).first()
        return model.to_entity() if model else None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[{Entity}]:
        models = self._db.query({Entity}Model).offset(skip).limit(limit).all()
        return [m.to_entity() for m in models]

    def create(self, entity: {Entity}) -> {Entity}:
        model = {Entity}Model.from_entity(entity)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return model.to_entity()

    def update(self, entity: {Entity}) -> {Entity}:
        model = self._db.query({Entity}Model).filter({Entity}Model.id == entity.id).first()
        if model:
            model.name = entity.name
            model.status = entity.status.value if entity.status else model.status
            self._db.commit()
            self._db.refresh(model)
            return model.to_entity()
        return None

    def delete(self, id: int) -> bool:
        model = self._db.query({Entity}Model).filter({Entity}Model.id == id).first()
        if model:
            self._db.delete(model)
            self._db.commit()
            return True
        return False
```

### 6. 生成接口层代码

**路由模板**:
```python
# interfaces/api/routes/{module}_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.{module}.application.{module}_service import {Module}Service
from app.modules.{module}.infrastructure.persistence.repositories.{entity}_repository_impl import {Entity}RepositoryImpl
from app.modules.{module}.interfaces.api.schemas.{module}_schemas import (
    Create{Entity}Request,
    Update{Entity}Request,
    {Entity}Response
)

router = APIRouter(prefix="/{module}s", tags=["{模块}"])


def get_{module}_service(db: Session = Depends(get_db)) -> {Module}Service:
    """依赖注入：获取应用服务"""
    {entity}_repo = {Entity}RepositoryImpl(db)
    return {Module}Service({entity}_repo={entity}_repo)


@router.post("", response_model={Entity}Response, status_code=status.HTTP_201_CREATED)
def create_{entity}(
    request: Create{Entity}Request,
    service: {Module}Service = Depends(get_{module}_service)
):
    """创建{实体}"""
    from app.modules.{module}.application.dtos.{module}_dtos import Create{Entity}DTO
    dto = Create{Entity}DTO(**request.dict())
    return service.create_{entity}(dto)


@router.get("", response_model=List[{Entity}Response])
def list_{entity}s(
    skip: int = 0,
    limit: int = 100,
    service: {Module}Service = Depends(get_{module}_service)
):
    """获取{实体}列表"""
    return service.list_{entity}s(skip=skip, limit=limit)


@router.get("/{entity_id}", response_model={Entity}Response)
def get_{entity}(
    {entity}_id: int,
    service: {Module}Service = Depends(get_{module}_service)
):
    """获取{实体}详情"""
    result = service.get_{entity}({entity}_id)
    if not result:
        raise HTTPException(status_code=404, detail="{实体}不存在")
    return result


@router.put("/{entity_id}", response_model={Entity}Response)
def update_{entity}(
    {entity}_id: int,
    request: Update{Entity}Request,
    service: {Module}Service = Depends(get_{module}_service)
):
    """更新{实体}"""
    from app.modules.{module}.application.dtos.{module}_dtos import Update{Entity}DTO
    dto = Update{Entity}DTO(**request.dict(exclude_unset=True))
    result = service.update_{entity}({entity}_id, dto)
    if not result:
        raise HTTPException(status_code=404, detail="{实体}不存在")
    return result


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{entity}(
    {entity}_id: int,
    service: {Module}Service = Depends(get_{module}_service)
):
    """删除{实体}"""
    success = service.delete_{entity}({entity}_id)
    if not success:
        raise HTTPException(status_code=404, detail="{实体}不存在")
```

**Schema 模板**:
```python
# interfaces/api/schemas/{module}_schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Create{Entity}Request(BaseModel):
    """创建{实体}请求"""
    name: str
    description: Optional[str] = None


class Update{Entity}Request(BaseModel):
    """更新{实体}请求"""
    name: Optional[str] = None
    description: Optional[str] = None


class {Entity}Response(BaseModel):
    """{实体}响应"""
    id: int
    name: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 7. 生成模块组装文件

```python
# __init__.py
from fastapi import APIRouter

from app.modules.{module}.interfaces.api.routes.{module}_routes import router as {module}_router

# 导出路由
router = {module}_router

# 导出应用服务（供其他模块使用）
from app.modules.{module}.application.{module}_service import {Module}Service
```

## 示例

### 示例：生成验证执行模块

```
/skill:generate-ddd-scaffold --prd=Module_04_Verification_Execution.md --with-tests
```

**预期输出**:
```
📖 解析 PRD: Module_04_Verification_Execution.md
   • 模块名称: verification
   • 识别实体: VerificationTask, VerificationRecord, VerificationScript
   • 识别值对象: VerificationStatus, VerificationMethod
   • 识别接口: 12 个 REST API

🏗️  生成 DDD 代码骨架:
   ✓ domain/entities/verification_task.py
   ✓ domain/entities/verification_record.py
   ✓ domain/entities/verification_script.py
   ✓ domain/value_objects/verification_status.py
   ✓ domain/value_objects/verification_method.py
   ✓ domain/repositories/verification_task_repository.py
   ✓ domain/repositories/verification_record_repository.py
   ✓ domain/repositories/verification_script_repository.py
   ✓ application/dtos/verification_dtos.py
   ✓ application/verification_service.py
   ✓ infrastructure/persistence/models/verification_task_model.py
   ✓ infrastructure/persistence/models/verification_record_model.py
   ✓ infrastructure/persistence/models/verification_script_model.py
   ✓ infrastructure/persistence/repositories/verification_task_repository_impl.py
   ✓ infrastructure/persistence/repositories/verification_record_repository_impl.py
   ✓ infrastructure/persistence/repositories/verification_script_repository_impl.py
   ✓ interfaces/api/routes/verification_routes.py
   ✓ interfaces/api/schemas/verification_schemas.py
   ✓ __init__.py

🧪 生成测试骨架:
   ✓ tests/unit/test_verification_domain.py
   ✓ tests/unit/test_verification_service.py
   ✓ tests/integration/api/test_verification_api.py

📋 下一步:
   1. 检查生成的代码，根据业务逻辑完善实体方法
   2. 在 main.py 中注册路由
   3. 运行数据库迁移
   4. 使用 /skill:api-integration-test 进行联调测试
```

## 注意事项

1. 生成的代码是基础骨架，需要根据实际业务逻辑完善
2. 跨模块依赖需要手动在应用服务中注入
3. 复杂业务规则需要在领域服务中实现
4. 生成后务必检查类型注解和导入语句
