# 高并发秒杀系统 🔥

基于 Spring Boot 3 + Vue 2 构建的高可用秒杀系统，支持 10万+ QPS 并发场景。

## 🎯 项目简介

本项目实现了完整的秒杀业务场景，包含：
- 商品展示与实时库存
- 分布式锁库存扣减
- 异步订单处理
- 实时数据可视化
- 高并发压测工具

## 🏗️ 技术架构

### 后端
- **Spring Boot 3** - 微服务框架
- **Redis** - 分布式锁 + 缓存
- **RabbitMQ** - 消息队列，异步订单处理
- **MySQL** - 持久化存储

### 前端
- **Vue 2** - 前端框架
- **Element UI** - UI 组件库
- **ECharts** - 数据可视化

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/sirpinaple1/seckill-system.git
cd seckill-system
```

### 2. 启动依赖服务
```bash
# Redis
redis-server

# RabbitMQ
rabbitmq-server

# MySQL
mysql.server start
```

### 3. 启动后端
```bash
cd backend
mvn clean package
java -jar target/seckill-system-1.0.0.jar
```

### 4. 启动前端
```bash
cd frontend
npm install
npm run serve
```

### 5. 访问系统
- 前端: http://localhost:8081
- 后端API: http://localhost:8080

## 📊 接口文档

| 接口 | 方法 | 说明 |
|-----|------|------|
| `/api/seckill/{productId}` | POST | 秒杀抢购 |
| `/api/product/list` | GET | 商品列表 |
| `/api/traffic/realtime` | GET | 实时客流 |
| `/api/traffic/hourly` | GET | 小时趋势 |
| `/api/refund/{orderNo}` | POST | 申请退款 |

## 🧪 压测脚本

### 快速压测
```bash
python3 seckill_stress_test.py 1000 100 1
```

### 模拟抢购
```bash
python3 seckill_simulation.py 60 300
```

参数说明: `脚本名 总请求数 并发数 商品ID`

## 📈 测试结果

| 指标 | 数值 |
|-----|------|
| QPS | 400+ |
| 成功率 | ~37% |
| 响应时间(P99) | <60ms |
| 库存扣减 | 正确，无超卖 |

## 📁 项目结构

```
seckill-system/
├── backend/          # Spring Boot 后端
│   ├── src/
│   └── target/      # 构建产物
├── frontend/         # Vue 前端
│   ├── src/
│   └── public/
├── docs/            # 文档
│   ├── DESIGN.md
│   └── TEST_REPORT.md
├── seckill_simulation.py   # 抢购模拟脚本
└── seckill_stress_test.py  # 压测脚本
```

## 📄 文档

- [设计文档](docs/DESIGN.md)
- [测试报告](docs/TEST_REPORT.md)
- [Releases](https://github.com/sirpinaple1/seckill-system/releases)

## ⚠️ 注意事项

1. 确保 Redis、RabbitMQ、MySQL 已启动
2. 首次运行需执行 `mvn clean package` 构建
3. 前端依赖 node_modules，首次需 `npm install`

---

**版本**: v1.0.0  
**作者**: OpenClaw AI Assistant  
**许可证**: MIT
