# 车队调度与维护管理平台

## Docker 快速启动

```bash
cp .env.example .env
docker compose up -d
```

前端：http://localhost:18708  
后端：http://localhost:19208/api/health/

## 项目介绍

面向物流公司和车队管理者的全栈 Web 应用，覆盖车辆档案、司机管理、调度派单、油耗统计和维保记录。

## 主要功能

- 调度中心：创建调度单、指派车辆和司机、开始/完成/取消运输、已指派单据改派、运输时间线。
- 车辆管理：车辆卡片、维保历史、油耗趋势入口。
- 司机管理：状态筛选、调度历史、驾驶时长统计。
- 维保管理：维修日历、费用统计、到期高亮。
- 油耗分析：油耗趋势、月度总油耗、异常油耗预警。

## 派单闭环规则（持久化）

创建调度单时后端强制校验，任一不满足都会返回明确原因：

| 校验项 | 规则 | 失败响应 |
| --- | --- | --- |
| 车辆状态 | 必须为 `Available` | 409 `DISPATCH_CONFLICT` |
| 车辆载重 | 额定载重 ≥ 货物重量 | 400 `VEHICLE_PAYLOAD_INSUFFICIENT` |
| 车辆保险 | 保险到期日不早于当天 | 400 `VEHICLE_INSURANCE_EXPIRED` |
| 司机状态 | 必须为 `Available` | 409 `DISPATCH_CONFLICT` |
| 司机证件 | 驾照到期日不早于当天 | 400 `DRIVER_LICENSE_EXPIRED` |
| 资源占用 | 同一车辆/司机已有未结束单据（Assigned/InProgress）即拒绝 | 409 `DISPATCH_CONFLICT` |

状态流转：`Assigned --开始--> InProgress --完成--> Completed`，`Assigned/InProgress --取消--> Cancelled`。

- 开始运输：单据变 `InProgress`，车辆与司机同步切换 `OnTrip`。
- 完成 / 取消：单据结束，车辆与司机恢复 `Available`。
- 运输中（InProgress）的单据不得改派；任何状态不得重复开始/完成/取消。
- 并发分配由事务 + 行锁（PostgreSQL `SELECT FOR UPDATE`）+ 部分唯一约束三重防护，冲突返回 409。
- 所有状态变化写入 `DispatchEvent` 时间线及各状态时间戳，数据落 PostgreSQL 命名卷，**服务重启后状态、占用关系与时间线仍可查询**。

调度接口（均返回 JSON，错误体为 `{"code": "...", "reason": "..."}`）：

```
POST   /api/dispatch-orders/                 创建并指派
GET    /api/dispatch-orders/?status=InProgress
POST   /api/dispatch-orders/{id}/start/      开始运输
POST   /api/dispatch-orders/{id}/complete/   完成运输
POST   /api/dispatch-orders/{id}/cancel/     取消单据
POST   /api/dispatch-orders/{id}/reassign/   改派（仅 Assigned）
```

后端容器启动时自动执行 `migrate` 并通过幂等的 `seed_demo` 写入演示车辆/司机（含保险过期、载重不足、维保中等场景）。

## 本地开发

后端默认监听 3000，前端开发服务器会把 `/api` 请求代理到后端。后端本地启动需要可连接的 PostgreSQL；如果没有本机 PostgreSQL，请优先使用 Docker Compose 启动完整环境。

```bash
cd backend
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:3000
```

```bash
cd frontend
npm install
npm run dev
```

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | React 18 + TypeScript + Vite |
| UI | Ant Design 5 |
| 图表 | ECharts |
| 状态 | Zustand |
| 后端 | Django + Django REST Framework |
| 数据库 | PostgreSQL 15 |
| 认证 | SimpleJWT |

## 目录结构

```
frontend/src/
├── api/ stores/ types/ components/common/ hooks/ pages/ router/ utils/ constants/
backend/
├── fleet_app/views/ serializers/ services/ middleware/ models.py urls.py permissions.py admin.py
└── config/settings.py urls.py
```

## 环境变量

| 变量 | 说明 |
| --- | --- |
| COMPOSE_PROJECT_NAME | Docker Compose 项目名 |
| DB_NAME / DB_USER / DB_PASSWORD / DB_ROOT_PASSWORD | PostgreSQL 配置 |
| JWT_SECRET | JWT 密钥 |
| FRONTEND_PORT / BACKEND_PORT | 宿主机端口 |

## 枚举位置

- VehicleStatus：frontend/src/types/enums.ts；frontend/src/types/vehicle.ts；frontend/src/components/common/VehicleCard.tsx；backend/fleet_app/models.py；backend/fleet_app/services/vehicle_service.py
- DispatchStatus：frontend/src/types/enums.ts；frontend/src/types/dispatch.ts；frontend/src/hooks/useDispatch.ts；backend/fleet_app/models.py；backend/fleet_app/services/dispatch_service.py
- MaintenanceType：frontend/src/types/enums.ts；frontend/src/types/maintenance.ts；frontend/src/pages/MaintenanceManage.tsx；backend/fleet_app/models.py；backend/fleet_app/services/maintenance_service.py
- DriverStatus：frontend/src/types/enums.ts；frontend/src/types/driver.ts；backend/fleet_app/models.py；backend/fleet_app/services/driver_service.py

## License

MIT
