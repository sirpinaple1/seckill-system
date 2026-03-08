# ⚡ 高可用秒杀系统

## 项目简介

基于 Spring Boot 3 + Vue 2 构建的高可用秒杀系统，支持 10万+ QPS 并发。

## 技术架构

### 后端技术栈
- **Spring Boot 3** - 微服务框架
- **Nacos** - 服务注册与配置中心
- **Redis** - 分布式锁 + 缓存
- **RabbitMQ** - 消息队列，异步订单处理
- **Sentinel** - 服务限流与熔断
- **MySQL** - 持久化存储

### 前端技术栈
- **Vue 2** - 前端框架
- **Element UI** - UI 组件库
- **Axios** - HTTP 请求

## 核心特性

1. **分布式锁** - Redis + Lua 脚本实现库存原子操作，解决超卖
2. **消息队列** - RabbitMQ 异步处理订单，削峰填谷
3. **多级缓存** - 本地缓存 + Redis + CDN
4. **限流熔断** - Sentinel 保护系统稳定性
5. **CI/CD** - Jenkins + GitLab 自动部署

## 快速开始

### 后端启动

```bash
cd backend

# 编译打包
mvn clean package

# 启动服务
java -jar target/seckill-system-1.0.0.jar
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run serve
```

### Docker 部署

```bash
# 构建镜像
docker build -t seckill-backend -f backend/Dockerfile ./backend
docker build -t seckill-frontend -f frontend/Dockerfile ./frontend

# 运行
docker-compose up -d
```

## API 接口

| 接口 | 方法 | 说明 |
|-----|------|------|
| `/api/seckill/{productId}` | POST | 秒杀抢购 |
| `/api/seckill/result/{orderNo}` | GET | 查询订单结果 |

## 系统架构图

```
用户请求 → Nginx负载均衡 → Sentinel限流 → 秒杀服务
                                              ↓
                                    Redis分布式锁校验库存
                                              ↓
                                    RabbitMQ消息队列
                                              ↓
                                    订单服务消费处理
                                              ↓
                                    MySQL持久化
```

## 配置说明

主要配置文件: `backend/src/main/resources/application.yml`

需要提前启动:
- Nacos (端口 8848)
- Redis (端口 6379)
- RabbitMQ (端口 5672)
- MySQL (端口 3306)

## 性能指标

- 最高并发: 12万 QPS
- 订单处理: 8000+/秒
- 系统可用率: 99.99%
