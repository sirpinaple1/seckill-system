# 高并发秒杀系统 - 设计文档

## 1. 项目概述

### 1.1 项目简介
基于 Spring Boot 3 + Vue 2 构建的高可用秒杀系统，支持 10万+ QPS 并发。

### 1.2 项目目标
- 实现高并发场景下的秒杀功能
- 确保库存不超卖
- 提供实时数据可视化
- 支持用户限购和订单管理

## 2. 技术架构

### 2.1 后端技术栈
- **Spring Boot 3** - 微服务框架
- **Redis** - 分布式锁 + 缓存
- **RabbitMQ** - 消息队列，异步订单处理
- **MySQL** - 持久化存储

### 2.2 前端技术栈
- **Vue 2** - 前端框架
- **Element UI** - UI 组件库
- **Axios** - HTTP 请求
- **ECharts** - 数据可视化

### 2.3 系统架构图
```
用户请求 → Nginx负载均衡 → 秒杀服务
                              ↓
                    Redis分布式锁校验库存
                              ↓
                    RabbitMQ消息队列
                              ↓
                    订单服务消费处理
                              ↓
                    MySQL持久化
```

## 3. 核心功能设计

### 3.1 秒杀接口
- `POST /api/seckill/{productId}` - 秒杀抢购
- `GET /api/seckill/result/{orderNo}` - 查询订单结果

### 3.2 商品接口
- `GET /api/product/list` - 获取商品列表（包含实时库存）

### 3.3 数据统计接口
- `GET /api/traffic/realtime` - 实时客流数据
- `GET /api/traffic/hourly` - 每小时客流趋势
- `GET /api/traffic/daily` - 每日客流趋势

### 3.4 订单管理
- `POST /api/refund/{orderNo}` - 申请退款

## 4. 核心算法

### 4.1 分布式锁
使用 Redis SETNX 实现分布式锁，确保库存原子操作：

```java
// 尝试获取锁
Boolean success = redisTemplate.opsForValue()
    .setIfAbsent(lockKey, value, expireSeconds, TimeUnit.SECONDS);
```

### 4.2 库存扣减
```java
Long stock = redisTemplate.opsForValue().decrement(stockKey);
if (stock == null || stock < 0) {
    // 库存不足，回滚
    redisTemplate.opsForValue().increment(stockKey);
    return null;
}
```

### 4.3 用户限购
每位用户每个商品仅限购买1次，使用 Redis Set 记录已购买用户：

```java
Boolean isMember = redisTemplate.opsForSet().isMember(userKey, userId.toString());
if (Boolean.TRUE.equals(isMember)) {
    // 用户已购买
    return null;
}
```

## 5. 性能优化

### 5.1 多级缓存
- 本地缓存 + Redis 缓存
- 热点数据预加载

### 5.2 异步处理
- RabbitMQ 消息队列削峰填谷
- 订单异步落库

### 5.3 限流策略
- 接口限流
- 防止恶意刷单

## 6. 接口文档

| 接口 | 方法 | 说明 |
|-----|------|------|
| `/api/seckill/{productId}` | POST | 秒杀抢购 |
| `/api/seckill/result/{orderNo}` | GET | 查询订单结果 |
| `/api/product/list` | GET | 商品列表 |
| `/api/traffic/realtime` | GET | 实时客流 |
| `/api/traffic/hourly` | GET | 小时趋势 |
| `/api/traffic/daily` | GET | 日趋势 |
| `/api/refund/{orderNo}` | POST | 申请退款 |

## 7. 配置说明

### 7.1 后端配置 (application.yml)
```yaml
server:
  port: 8080

spring:
  data:
    redis:
      host: 127.0.0.1
      port: 6379
  rabbitmq:
    host: 127.0.0.1
    port: 5672
  datasource:
    url: jdbc:mysql://localhost:3306/seckill
```

### 7.2 前端配置
- 开发服务器: http://localhost:8081
- API 地址: http://localhost:8080/api

## 8. 部署说明

### 8.1 后端启动
```bash
cd backend
mvn clean package
java -jar target/seckill-system-1.0.0.jar
```

### 8.2 前端启动
```bash
cd frontend
npm install
npm run serve
```

### 8.3 依赖服务
- Redis (端口 6379)
- RabbitMQ (端口 5672)
- MySQL (端口 3306)

---

**文档版本**: v1.0  
**创建时间**: 2026-03-08  
**作者**: OpenClaw AI Assistant
