#!/usr/bin/env python3
"""
测试数据初始化脚本
为计划管理(plan)和台账管理(inventory)模块添加测试数据
"""
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal, Base, engine
from app.modules.inventory.infrastructure.persistence.models.inventory_model import (
    ApplicationModel,
    CloudResourceModel,
    AccountModel,
    PlanInventoryLinkModel,
)
from app.modules.plan.infrastructure.persistence.models.plan_model import (
    PlanModel,
    PlanInventoryLinkModel as PlanLinkModel,
)


def generate_plan_id(date: datetime, seq: int) -> str:
    """生成计划ID"""
    return f"PLAN-{date.strftime('%Y%m%d')}-{seq:03d}"


def generate_data_tag(plan_id: str, category: str) -> str:
    """生成数据标签"""
    category_map = {
        'new_system': 'NEW',
        'new_feature': 'FTR',
        'func_change': 'FUN',
        'arch_change': 'ARC',
        'security_check': 'SEC',
    }
    timestamp = int(datetime.utcnow().timestamp())
    return f"{plan_id}-{category_map.get(category, 'UNK')}-{timestamp}"


def seed_applications(db) -> list:
    """创建应用系统台账测试数据"""
    print("📱 创建应用系统台账...")
    
    applications = [
        {
            "id": str(uuid4()),
            "app_name": "订单管理系统",
            "app_description": "核心业务订单管理系统，处理订单全生命周期",
            "function_modules": [
                {"module_name": "订单中心", "launch_time": "2024-01-15"},
                {"module_name": "支付网关", "launch_time": "2024-01-15"},
                {"module_name": "退款管理", "launch_time": "2024-03-01"},
            ],
            "hostname": "order-prod-01",
            "app_url": "https://order.example.com",
            "business_owner": "张三",
            "project_owner": "李四",
            "launch_time": datetime(2024, 1, 15),
            "status": "active",
            "related_plan_ids": [],
            "created_by": "admin",
        },
        {
            "id": str(uuid4()),
            "app_name": "用户中心",
            "app_description": "统一用户认证和权限管理中心",
            "function_modules": [
                {"module_name": "用户认证", "launch_time": "2023-06-01"},
                {"module_name": "权限管理", "launch_time": "2023-06-01"},
                {"module_name": "组织架构", "launch_time": "2023-09-01"},
            ],
            "hostname": "user-prod-01",
            "app_url": "https://user.example.com",
            "business_owner": "王五",
            "project_owner": "赵六",
            "launch_time": datetime(2023, 6, 1),
            "status": "active",
            "related_plan_ids": [],
            "created_by": "admin",
        },
        {
            "id": str(uuid4()),
            "app_name": "库存管理系统",
            "app_description": "实时库存管理和预警系统",
            "function_modules": [
                {"module_name": "库存查询", "launch_time": "2024-02-01"},
                {"module_name": "入库管理", "launch_time": "2024-02-01"},
                {"module_name": "出库管理", "launch_time": "2024-02-01"},
                {"module_name": "库存预警", "launch_time": "2024-03-15"},
            ],
            "hostname": "stock-prod-01",
            "app_url": "https://stock.example.com",
            "business_owner": "孙七",
            "project_owner": "周八",
            "launch_time": datetime(2024, 2, 1),
            "status": "active",
            "related_plan_ids": [],
            "created_by": "admin",
        },
        {
            "id": str(uuid4()),
            "app_name": "数据分析平台",
            "app_description": "业务数据分析和报表平台",
            "function_modules": [
                {"module_name": "数据采集", "launch_time": "2023-12-01"},
                {"module_name": "报表中心", "launch_time": "2023-12-01"},
                {"module_name": "数据可视化", "launch_time": "2024-01-01"},
            ],
            "hostname": "data-prod-01",
            "app_url": "https://data.example.com",
            "business_owner": "吴九",
            "project_owner": "郑十",
            "launch_time": datetime(2023, 12, 1),
            "status": "inactive",
            "related_plan_ids": [],
            "created_by": "admin",
        },
    ]
    
    app_models = []
    for app_data in applications:
        app = ApplicationModel(**app_data)
        db.add(app)
        app_models.append(app)
    
    db.commit()
    print(f"   ✅ 创建了 {len(app_models)} 个应用系统")
    return app_models


def seed_cloud_resources(db, applications: list):
    """创建云资源台账测试数据"""
    print("☁️ 创建云资源台账...")
    
    resources = []
    
    # 订单管理系统的资源
    order_app = next((a for a in applications if a.app_name == "订单管理系统"), None)
    if order_app:
        resources.extend([
            {
                "id": str(uuid4()),
                "app_id": order_app.id,
                "resource_type": "compute",
                "resource_name": "order-ecs-prod-01",
                "configuration": {
                    "instance_type": "ecs.g7.xlarge",
                    "cpu": 4,
                    "memory": 16,
                    "os": "CentOS 7.9",
                    "region": "cn-hangzhou",
                },
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
            {
                "id": str(uuid4()),
                "app_id": order_app.id,
                "resource_type": "database",
                "resource_name": "order-rds-prod",
                "configuration": {
                    "engine": "MySQL",
                    "version": "8.0",
                    "instance_type": "rds.mysql.c1.large",
                    "storage": 100,
                    "region": "cn-hangzhou",
                },
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
            {
                "id": str(uuid4()),
                "app_id": order_app.id,
                "resource_type": "network",
                "resource_name": "order-slb-prod",
                "configuration": {
                    "type": "application",
                    "bandwidth": 100,
                    "region": "cn-hangzhou",
                },
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
        ])
    
    # 用户中心的资源
    user_app = next((a for a in applications if a.app_name == "用户中心"), None)
    if user_app:
        resources.extend([
            {
                "id": str(uuid4()),
                "app_id": user_app.id,
                "resource_type": "compute",
                "resource_name": "user-ecs-prod-01",
                "configuration": {
                    "instance_type": "ecs.g7.large",
                    "cpu": 2,
                    "memory": 8,
                    "os": "Alibaba Cloud Linux 3",
                    "region": "cn-beijing",
                },
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
            {
                "id": str(uuid4()),
                "app_id": user_app.id,
                "resource_type": "database",
                "resource_name": "user-redis-prod",
                "configuration": {
                    "engine": "Redis",
                    "version": "6.0",
                    "instance_type": "redis.master.small.default",
                    "region": "cn-beijing",
                },
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
            {
                "id": str(uuid4()),
                "app_id": user_app.id,
                "resource_type": "cache",
                "resource_name": "user-memcached-prod",
                "configuration": {
                    "engine": "Memcached",
                    "version": "1.6",
                    "capacity": 1024,
                    "region": "cn-beijing",
                },
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
        ])
    
    # 库存管理系统的资源
    stock_app = next((a for a in applications if a.app_name == "库存管理系统"), None)
    if stock_app:
        resources.extend([
            {
                "id": str(uuid4()),
                "app_id": stock_app.id,
                "resource_type": "compute",
                "resource_name": "stock-ecs-prod-01",
                "configuration": {
                    "instance_type": "ecs.c7.xlarge",
                    "cpu": 4,
                    "memory": 8,
                    "os": "CentOS 8.2",
                    "region": "cn-shanghai",
                },
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
            {
                "id": str(uuid4()),
                "app_id": stock_app.id,
                "resource_type": "database",
                "resource_name": "stock-mongodb-prod",
                "configuration": {
                    "engine": "MongoDB",
                    "version": "5.0",
                    "instance_type": "dds.mongo.standard",
                    "storage": 500,
                    "region": "cn-shanghai",
                },
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
            {
                "id": str(uuid4()),
                "app_id": stock_app.id,
                "resource_type": "message_queue",
                "resource_name": "stock-kafka-prod",
                "configuration": {
                    "engine": "Kafka",
                    "version": "2.6",
                    "instance_type": "kafka.standard",
                    "partitions": 12,
                    "region": "cn-shanghai",
                },
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
        ])
    
    for res_data in resources:
        res = CloudResourceModel(**res_data)
        db.add(res)
    
    db.commit()
    print(f"   ✅ 创建了 {len(resources)} 个云资源")


def seed_accounts(db, applications: list):
    """创建账号台账测试数据"""
    print("👤 创建账号台账...")
    
    accounts = []
    now = datetime.utcnow()
    
    # 订单管理系统的账号
    order_app = next((a for a in applications if a.app_name == "订单管理系统"), None)
    if order_app:
        accounts.extend([
            {
                "id": str(uuid4()),
                "app_id": order_app.id,
                "account_type": "system",
                "account_name": "order-service",
                "permission_level": "execute",
                "holder_name": "运维组",
                "valid_from": now - timedelta(days=90),
                "valid_until": now + timedelta(days=275),
                "password_change_cycle": 90,
                "last_password_change": now - timedelta(days=30),
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
            {
                "id": str(uuid4()),
                "app_id": order_app.id,
                "account_type": "software",
                "account_name": "order_admin",
                "permission_level": "admin",
                "holder_name": "张三",
                "valid_from": now - timedelta(days=180),
                "valid_until": now + timedelta(days=185),
                "password_change_cycle": 60,
                "last_password_change": now - timedelta(days=10),
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
            {
                "id": str(uuid4()),
                "app_id": order_app.id,
                "account_type": "database",
                "account_name": "order_db_user",
                "permission_level": "write",
                "holder_name": "数据库组",
                "valid_from": now - timedelta(days=365),
                "valid_until": now + timedelta(days=30),  # 即将过期
                "password_change_cycle": 90,
                "last_password_change": now - timedelta(days=5),
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
        ])
    
    # 用户中心的账号
    user_app = next((a for a in applications if a.app_name == "用户中心"), None)
    if user_app:
        accounts.extend([
            {
                "id": str(uuid4()),
                "app_id": user_app.id,
                "account_type": "system",
                "account_name": "user-service",
                "permission_level": "execute",
                "holder_name": "运维组",
                "valid_from": now - timedelta(days=200),
                "valid_until": now + timedelta(days=165),
                "password_change_cycle": 90,
                "last_password_change": now - timedelta(days=45),
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
            {
                "id": str(uuid4()),
                "app_id": user_app.id,
                "account_type": "software",
                "account_name": "user_manager",
                "permission_level": "admin",
                "holder_name": "王五",
                "valid_from": now - timedelta(days=150),
                "valid_until": now - timedelta(days=10),  # 已过期
                "password_change_cycle": 60,
                "last_password_change": now - timedelta(days=20),
                "status": "expired",
                "related_plan_ids": [],
                "created_by": "admin",
            },
        ])
    
    # 库存管理系统的账号
    stock_app = next((a for a in applications if a.app_name == "库存管理系统"), None)
    if stock_app:
        accounts.extend([
            {
                "id": str(uuid4()),
                "app_id": stock_app.id,
                "account_type": "system",
                "account_name": "stock-service",
                "permission_level": "execute",
                "holder_name": "运维组",
                "valid_from": now - timedelta(days=60),
                "valid_until": now + timedelta(days=305),
                "password_change_cycle": 90,
                "last_password_change": now,
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
            {
                "id": str(uuid4()),
                "app_id": stock_app.id,
                "account_type": "database",
                "account_name": "stock_readonly",
                "permission_level": "read",
                "holder_name": "数据分析师",
                "valid_from": now - timedelta(days=30),
                "valid_until": now + timedelta(days=335),
                "password_change_cycle": 90,
                "last_password_change": now - timedelta(days=85),  # 密码即将过期
                "status": "active",
                "related_plan_ids": [],
                "created_by": "admin",
            },
        ])
    
    for acc_data in accounts:
        acc = AccountModel(**acc_data)
        db.add(acc)
    
    db.commit()
    print(f"   ✅ 创建了 {len(accounts)} 个账号")


def seed_plans(db, applications: list):
    """创建计划测试数据"""
    print("📋 创建计划...")
    
    now = datetime.utcnow()
    plans = []
    
    # 获取应用ID
    order_app = next((a for a in applications if a.app_name == "订单管理系统"), None)
    user_app = next((a for a in applications if a.app_name == "用户中心"), None)
    stock_app = next((a for a in applications if a.app_name == "库存管理系统"), None)
    
    # 计划1: 新系统上线 - 已完成
    plan1_id = generate_plan_id(now, 1)
    plans.append({
        "id": plan1_id,
        "data_tag": generate_data_tag(plan1_id, "new_system"),
        "name": "订单管理系统v2.0上线",
        "category": "new_system",
        "priority": 0,  # P0
        "description": "订单管理系统全新版本上线，包含支付模块重构",
        "planned_start_time": now - timedelta(days=30),
        "planned_end_time": now - timedelta(days=25),
        "actual_start_time": now - timedelta(days=30),
        "actual_end_time": now - timedelta(days=26),
        "status": "COMPLETED",
        "workflow_template_id": "SOP-NEW-001",
        "inventory_action": "create_new",
        "approval_files": ["file-001.pdf", "file-002.pdf"],
        "created_by": "admin",
    })
    
    # 计划2: 新功能上线 - 进行中
    plan2_id = generate_plan_id(now, 2)
    plans.append({
        "id": plan2_id,
        "data_tag": generate_data_tag(plan2_id, "new_feature"),
        "name": "用户中心新增组织架构功能",
        "category": "new_feature",
        "priority": 1,  # P1
        "description": "在用户中心新增组织架构管理功能模块",
        "planned_start_time": now - timedelta(days=5),
        "planned_end_time": now + timedelta(days=10),
        "actual_start_time": now - timedelta(days=5),
        "status": "IN_PROGRESS",
        "workflow_template_id": "SOP-FTR-001",
        "inventory_action": "select_and_edit",
        "approval_files": ["file-003.pdf"],
        "created_by": "admin",
    })
    
    # 计划3: 功能变更 - 草稿
    plan3_id = generate_plan_id(now, 3)
    plans.append({
        "id": plan3_id,
        "data_tag": generate_data_tag(plan3_id, "func_change"),
        "name": "库存预警规则优化",
        "category": "func_change",
        "priority": 2,  # P2
        "description": "优化库存预警触发规则和通知方式",
        "planned_start_time": now + timedelta(days=7),
        "planned_end_time": now + timedelta(days=14),
        "status": "DRAFT",
        "workflow_template_id": "SOP-FUN-001",
        "inventory_action": "select_existing",
        "approval_files": [],
        "created_by": "admin",
    })
    
    # 计划4: 架构变更 - 待执行
    plan4_id = generate_plan_id(now, 4)
    plans.append({
        "id": plan4_id,
        "data_tag": generate_data_tag(plan4_id, "arch_change"),
        "name": "订单系统数据库迁移",
        "category": "arch_change",
        "priority": 0,  # P0
        "description": "将订单系统数据库从MySQL 5.7迁移到MySQL 8.0",
        "planned_start_time": now + timedelta(days=3),
        "planned_end_time": now + timedelta(days=5),
        "status": "PENDING",
        "workflow_template_id": "SOP-ARC-001",
        "inventory_action": "select_existing",
        "approval_files": ["file-004.pdf", "file-005.pdf"],
        "created_by": "admin",
    })
    
    # 计划5: 安全检查 - 进行中
    plan5_id = generate_plan_id(now, 5)
    plans.append({
        "id": plan5_id,
        "data_tag": generate_data_tag(plan5_id, "security_check"),
        "name": "Q1季度安全巡检",
        "category": "security_check",
        "priority": 1,  # P1
        "description": "2024年第一季度全系统安全巡检",
        "planned_start_time": now - timedelta(days=2),
        "planned_end_time": now + timedelta(days=5),
        "actual_start_time": now - timedelta(days=2),
        "status": "IN_PROGRESS",
        "workflow_template_id": "SOP-SEC-001",
        "inventory_action": "security_scan",
        "approval_files": ["file-006.pdf"],
        "created_by": "admin",
    })
    
    # 计划6: 已取消
    plan6_id = generate_plan_id(now, 6)
    plans.append({
        "id": plan6_id,
        "data_tag": generate_data_tag(plan6_id, "func_change"),
        "name": "数据分析平台报表导出优化",
        "category": "func_change",
        "priority": 3,  # P3
        "description": "优化大数据量报表导出性能",
        "planned_start_time": now + timedelta(days=14),
        "planned_end_time": now + timedelta(days=21),
        "status": "CANCELLED",
        "workflow_template_id": "SOP-FUN-001",
        "inventory_action": "select_existing",
        "approval_files": [],
        "created_by": "admin",
    })
    
    for plan_data in plans:
        plan = PlanModel(**plan_data)
        db.add(plan)
    
    db.commit()
    print(f"   ✅ 创建了 {len(plans)} 个计划")
    
    # 创建计划与台账的关联
    print("🔗 创建计划与台账的关联...")
    links = []
    
    # 计划1关联订单管理系统
    if order_app:
        links.append({
            "plan_id": plan1_id,
            "inventory_id": order_app.id,
            "linked_at": now - timedelta(days=30),
        })
        # 更新应用的关联计划
        order_app.related_plan_ids = [plan1_id]
    
    # 计划2关联用户中心
    if user_app:
        links.append({
            "plan_id": plan2_id,
            "inventory_id": user_app.id,
            "linked_at": now - timedelta(days=5),
        })
        user_app.related_plan_ids = [plan2_id]
    
    # 计划3关联库存管理系统
    if stock_app:
        links.append({
            "plan_id": plan3_id,
            "inventory_id": stock_app.id,
            "linked_at": now,
        })
        stock_app.related_plan_ids = [plan3_id]
    
    # 计划4关联订单管理系统
    if order_app:
        links.append({
            "plan_id": plan4_id,
            "inventory_id": order_app.id,
            "linked_at": now,
        })
        order_app.related_plan_ids = order_app.related_plan_ids + [plan4_id]
    
    for link_data in links:
        link = PlanInventoryLinkModel(**link_data)
        db.add(link)
    
    db.commit()
    print(f"   ✅ 创建了 {len(links)} 个关联关系")


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 开始初始化测试数据")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 清空现有数据（可选，谨慎使用）
        print("\n🧹 清理现有数据...")
        db.query(PlanInventoryLinkModel).delete()
        db.query(PlanLinkModel).delete()
        db.query(AccountModel).delete()
        db.query(CloudResourceModel).delete()
        db.query(ApplicationModel).delete()
        db.query(PlanModel).delete()
        db.commit()
        print("   ✅ 清理完成")
        
        # 创建测试数据
        print("\n" + "=" * 60)
        print("📦 创建测试数据")
        print("=" * 60)
        
        # 1. 创建应用系统
        applications = seed_applications(db)
        
        # 2. 创建云资源
        seed_cloud_resources(db, applications)
        
        # 3. 创建账号
        seed_accounts(db, applications)
        
        # 4. 创建计划及关联
        seed_plans(db, applications)
        
        print("\n" + "=" * 60)
        print("✅ 测试数据初始化完成！")
        print("=" * 60)
        print("\n📊 数据统计:")
        print(f"   • 应用系统: {db.query(ApplicationModel).count()} 个")
        print(f"   • 云资源: {db.query(CloudResourceModel).count()} 个")
        print(f"   • 账号: {db.query(AccountModel).count()} 个")
        print(f"   • 计划: {db.query(PlanModel).count()} 个")
        print(f"   • 计划-台账关联: {db.query(PlanInventoryLinkModel).count()} 个")
        
        print("\n📋 计划状态分布:")
        from sqlalchemy import func
        status_counts = db.query(PlanModel.status, func.count()).group_by(PlanModel.status).all()
        for status, count in status_counts:
            print(f"   • {status}: {count} 个")
        
        print("\n📱 应用系统列表:")
        for app in db.query(ApplicationModel).all():
            plan_count = len(app.related_plan_ids) if app.related_plan_ids else 0
            print(f"   • {app.app_name} ({app.status}) - 关联 {plan_count} 个计划")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
