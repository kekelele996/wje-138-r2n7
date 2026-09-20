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

- 调度中心：创建调度单、指派车辆和司机、查看运输时间线。
- 车辆管理：车辆卡片、维保历史、油耗趋势入口。
- 司机管理：状态筛选、调度历史、驾驶时长统计。
- 维保管理：维修日历、费用统计、到期高亮。
- 油耗分析：油耗趋势、月度总油耗、异常油耗预警。

## 派单闭环（可持久化）

调度单状态机：`Assigned → InProgress → Completed`，`Assigned / InProgress → Cancelled`（`Completed / Cancelled` 为终态）。

- **创建（POST `/api/dispatch-orders/`）前置校验**
  - 车辆必须为 `Available`、保险到期日不早于当天、货物重量不超过核定载重（`loadCapacity`）
  - 司机驾照到期日不早于当天
  - 同一车辆或司机已存在未结束单据（`Assigned / InProgress`）时拒绝分配
- **开始运输**：`POST /api/dispatch-orders/{id}/start/`，车辆与司机同步切换为 `OnTrip`，记录实际出发时间
- **完成运输**：`POST /api/dispatch-orders/{id}/complete/`，车辆与司机恢复 `Available`，记录实际到达时间
- **取消**：`POST /api/dispatch-orders/{id}/cancel/`，车辆与司机恢复 `Available`
- 运输中（`InProgress`）及终态单据禁止重复操作；非法流转、资源冲突返回 `409` 与 JSON 原因 `{code, message}`
- 每次状态变化写入时间戳与 `DispatchStatusEvent` 事件流，落 PostgreSQL；后端重启后单据、状态与时间线仍可查询（前端「调度单详情 / 运输时间线」展示）
- 服务启动自动执行迁移并写入演示数据（可用/在途/维保车辆、证件与保险过期样例、一条在途单据和一条历史完成单据）

错误码示例：`vehicle_unavailable`、`vehicle_insurance_expired`、`load_exceeded`、`driver_license_expired`、`vehicle_busy`、`driver_busy`、`illegal_transition`、`duplicate_operation`、`already_finished`、`not_found`。

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

- VehicleStatus：frontend/src/types/enums.ts；frontend/src/types/vehicle.ts；frontend/src/components/common/VehicleCard.tsx；backend/fleet_app/enums.py；backend/fleet_app/models.py；backend/fleet_app/services/vehicle_service.py
- DispatchStatus：frontend/src/types/enums.ts（含 DispatchErrorCode）；frontend/src/types/dispatch.ts；frontend/src/hooks/useDispatch.ts；backend/fleet_app/enums.py；backend/fleet_app/models.py；backend/fleet_app/services/dispatch_service.py
- MaintenanceType：frontend/src/types/enums.ts；frontend/src/types/maintenance.ts；frontend/src/pages/MaintenanceManage.tsx；backend/fleet_app/enums.py；backend/fleet_app/models.py；backend/fleet_app/services/maintenance_service.py
- DriverStatus：frontend/src/types/enums.ts；frontend/src/types/driver.ts；backend/fleet_app/enums.py；backend/fleet_app/models.py；backend/fleet_app/services/driver_service.py

## License

MIT
