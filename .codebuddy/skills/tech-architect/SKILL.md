---
name: 技术架构师
description: 专业的技术架构师和技术负责人,精通系统架构设计、技术选型、微服务架构、性能优化、团队技术指导。适用于架构设计、技术决策、代码审查、技术规划等场景。
---

# 技术架构师技能

## 概述

本技能提供专业的技术架构和技术领导能力,涵盖从架构设计到团队技术管理的全流程。帮助构建可扩展、可维护、高性能的技术系统,并指导团队的技术发展。

## 核心能力

### 1. 系统架构设计

#### 架构设计原则

**SOLID原则**
- **单一职责原则(SRP)**: 每个模块只负责一个功能
- **开闭原则(OCP)**: 对扩展开放,对修改关闭
- **里氏替换原则(LSP)**: 子类可以替换父类
- **接口隔离原则(ISP)**: 接口应该小而专注
- **依赖倒置原则(DIP)**: 依赖抽象而非具体实现

**架构模式选择**
- **单体架构**: 小型应用,快速开发
- **分层架构**: 清晰的职责划分
- **微服务架构**: 大型系统,独立部署
- **事件驱动架构**: 松耦合,高扩展性
- **CQRS架构**: 读写分离,优化性能
- **六边形架构**: 领域驱动,可测试性高

#### 微服务架构设计

**服务拆分策略**
- 按业务领域拆分(Domain-Driven Design)
- 按功能拆分
- 按团队拆分(Conway's Law)
- 避免过度拆分和分布式事务

**服务通信**
- **同步通信**: REST API, gRPC
- **异步通信**: 消息队列,事件总线
- **服务发现**: Consul, Eureka, Nacos
- **API网关**: Kong, Zuul, Nginx

**数据一致性**
- **最终一致性**: BASE理论
- **分布式事务**: Saga模式, TCC
- **事件溯源**: Event Sourcing
- **CQRS**: 命令查询责任分离

### 2. 技术选型

#### 技术选型原则

**评估维度**
- **成熟度**: 社区活跃度、文档完善度
- **性能**: 响应时间、吞吐量、资源占用
- **可维护性**: 代码质量、架构清晰度
- **可扩展性**: 横向扩展、纵向扩展能力
- **团队熟悉度**: 学习成本、培训成本
- **生态丰富度**: 第三方库、工具支持
- **成本**: 开发成本、运维成本、授权成本

**技术栈选择**

**后端技术**
```markdown
- Web框架: FastAPI / Flask / Django / Spring Boot / NestJS
- 语言: Python / Java / Go / Node.js / Rust
- 数据库: PostgreSQL / MySQL / MongoDB / Redis
- ORM: SQLAlchemy / TypeORM / MyBatis / Prisma
- 消息队列: RabbitMQ / Kafka / Redis Pub/Sub
- 搜索引擎: Elasticsearch / Solr / MeiliSearch
```

**前端技术**
```markdown
- 框架: Vue 3 / React / Angular / Svelte
- 构建工具: Vite / Webpack / Rollup
- UI库: Element Plus / Ant Design / Material-UI / Tailwind CSS
- 状态管理: Pinia / Redux / Zustand / Jotai
```

**基础设施**
```markdown
- 容器: Docker / Kubernetes / Nomad
- 编排: Docker Compose / Kubernetes / Swarm
- CI/CD: GitHub Actions / GitLab CI / Jenkins
- 监控: Prometheus / Grafana / ELK / Datadog
- 服务网格: Istio / Linkerd / Consul Connect
```

#### 技术选型决策模板

```markdown
# [技术名称] 技术选型评估

## 需求分析
- 业务需求: [具体需求]
- 技术需求: [具体需求]
- 团队需求: [具体需求]

## 备选方案
1. [方案A]: 优点/缺点
2. [方案B]: 优点/缺点
3. [方案C]: 优点/缺点

## 评估矩阵
| 维度 | 方案A | 方案B | 方案C |
|------|-------|-------|-------|
| 成熟度 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 性能 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 可维护性 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 学习成本 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

## 决策
**选择方案**: [最终方案]
**理由**: [决策理由]
**风险**: [潜在风险]
**缓解措施**: [应对措施]
```

### 3. 性能优化

#### 性能优化策略

**数据库优化**
```sql
-- 索引优化
CREATE INDEX idx_user_email ON users(email);

-- 查询优化
SELECT id, name FROM users WHERE status = 'active' LIMIT 100;

-- 避免N+1查询
SELECT u.*, p.* FROM users u 
LEFT JOIN posts p ON u.id = p.user_id;

-- 分页查询
SELECT * FROM users 
ORDER BY id 
OFFSET 0 LIMIT 20;
```

**缓存策略**
- **本地缓存**: Caffeine, Guava Cache
- **分布式缓存**: Redis, Memcached
- **缓存模式**: Cache-Aside, Read-Through, Write-Through
- **缓存更新**: TTL, 主动更新, 懒加载

**异步处理**
- **异步任务**: Celery, RQ, Bull
- **事件驱动**: Kafka, RabbitMQ, NATS
- **异步IO**: asyncio, aiohttp, gevent

**负载均衡**
```yaml
# Nginx负载均衡配置
upstream backend {
    least_conn;
    server backend1:8000 weight=3;
    server backend2:8000 weight=2;
    server backend3:8000 backup;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}
```

#### 性能监控

**应用性能监控(APM)**
- **追踪**: Jaeger, Zipkin, SkyWalking
- **指标**: Prometheus, Grafana, InfluxDB
- **日志**: ELK Stack, Loki, Graylog
- **告警**: AlertManager, PagerDuty

**性能指标**
- **响应时间**: P50, P95, P99
- **吞吐量**: QPS, TPS, RPS
- **错误率**: HTTP 4xx/5xx, 异常率
- **资源使用**: CPU, 内存, 磁盘IO, 网络

### 4. 安全架构

#### 安全架构设计

**认证授权**
- **认证**: JWT, OAuth2, SAML, OpenID Connect
- **授权**: RBAC, ABAC, PBAC
- **会话管理**: Session, Token, Cookie
- **多因素认证**: 2FA, TOTP, 短信验证

**数据安全**
- **传输加密**: HTTPS, TLS, SSL
- **存储加密**: AES, RSA, 密码哈希
- **敏感数据脱敏**: 数据脱敏, 字段加密
- **数据备份**: 定期备份, 异地备份

**应用安全**
- **输入验证**: 参数校验, 类型检查, 长度限制
- **输出编码**: XSS防护, SQL注入防护, CSRF防护
- **依赖安全**: 依赖扫描, 定期更新, 漏洞修复
- **安全头**: CSP, X-Frame-Options, HSTS

**网络安全**
- **网络隔离**: VPC, 子网, 安全组
- **访问控制**: IP白名单, VPN, 防火墙
- **DDoS防护**: Cloudflare, AWS Shield, 阿里云DDoS
- **入侵检测**: IDS, IPS, WAF

#### 安全最佳实践

```python
# 安全配置示例
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# HTTPS重定向
app.add_middleware(HTTPSRedirectMiddleware)

# 可信主机
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 5. 可靠性设计

#### 高可用架构

**冗余设计**
- **服务冗余**: 多实例部署
- **数据冗余**: 主从复制, 多副本
- **网络冗余**: 多线路, 多ISP
- **机房冗余**: 多可用区, 多地域

**故障转移**
- **自动故障转移**: Keepalived, etcd
- **健康检查**: 探活检测, 心跳检测
- **熔断降级**: Hystrix, Sentinel
- **限流保护**: Nginx限流, 应用限流

#### 容灾备份

**备份策略**
- **全量备份**: 定期全量备份
- **增量备份**: 每小时增量备份
- **日志备份**: 实时binlog备份
- **异地备份**: 跨区域备份

**灾难恢复**
- **RPO (恢复点目标)**: 数据丢失容忍度
- **RTO (恢复时间目标)**: 服务恢复时间
- **演练计划**: 定期灾备演练
- **应急预案**: 紧急响应流程

### 6. 可扩展性设计

#### 水平扩展

**无状态服务**
```python
# 无状态设计示例
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.get_user(user_id)
    return user  # 服务无状态,可任意扩展实例
```

**数据库分片**
- **垂直分片**: 按业务拆分
- **水平分片**: 按数据范围拆分
- **一致性哈希**: 均匀分布数据
- **读写分离**: 主库写, 从库读

**缓存策略**
- **CDN缓存**: 静态资源缓存
- **应用缓存**: Redis分布式缓存
- **数据库缓存**: 查询结果缓存
- **页面缓存**: HTML缓存, 片段缓存

#### 垂直扩展

**资源优化**
- **CPU优化**: 算法优化, 并发处理
- **内存优化**: 内存池, 对象复用
- **IO优化**: 异步IO, 连接池
- **存储优化**: SSD, NVMe, 分布式存储

### 7. 代码审查

#### 代码审查标准

**代码质量**
- [ ] 符合编码规范(PEP8, ESLint)
- [ ] 命名清晰, 可读性强
- [ ] 逻辑清晰, 易于理解
- [ ] 注释充分, 文档完整
- [ ] 无硬编码, 配置化

**架构设计**
- [ ] 模块划分合理, 职责清晰
- [ ] 接口设计良好, 易于扩展
- [ ] 耦合度低, 内聚性高
- [ ] 错误处理完善
- [ ] 日志记录合理

**性能考虑**
- [ ] 算法复杂度合理
- [ ] 避免N+1查询
- [ ] 合理使用缓存
- [ ] 批量操作优化
- [ ] 异步处理恰当

**安全性**
- [ ] 输入验证完整
- [ ] 输出编码安全
- [ ] 认证授权正确
- [ ] 敏感数据保护
- [ ] 依赖包安全

#### 代码审查流程

1. **PR创建**: 开发者提交Pull Request
2. **自动检查**: CI自动运行测试和代码检查
3. **人工审查**: 至少一名reviewer审查
4. **修改迭代**: 根据反馈修改代码
5. **合并**: Review通过后合并代码

### 8. 技术规划

#### 技术路线图

**短期规划(1-3个月)**
- [ ] 技术债务清理
- [ ] 性能优化实施
- [ ] 安全加固
- [ ] 团队技能提升

**中期规划(3-6个月)**
- [ ] 架构升级重构
- [ ] 新技术引入
- [ ] 基础设施优化
- [ ] 开发效率提升

**长期规划(6-12个月)**
- [ ] 技术生态建设
- [ ] 系统演进方向
- [ ] 团队成长计划
- [ ] 技术品牌建设

#### 技术决策记录(ADR)

```markdown
# ADR-001: 选择FastAPI作为Web框架

## 状态
已接受

## 背景
需要选择一个高性能的Python Web框架用于新的API服务

## 决策
选择FastAPI作为主要Web框架

## 理由
1. 基于Starlette和Pydantic,性能优异
2. 自动生成API文档
3. 类型安全,支持异步
4. 社区活跃,文档完善
5. 团队已有使用经验

## 后果
- 正面: 开发效率高,类型安全
- 负面: 学习曲线,生态不如Django
```

### 9. 团队技术管理

#### 技术团队建设

**技术梯队**
- **初级工程师**: 基础开发任务
- **中级工程师**: 独立完成模块
- **高级工程师**: 技术难点攻关
- **技术专家**: 架构设计,技术决策

**技术分享**
- **技术分享会**: 定期内部分享
- **技术文档**: Wiki, 技术博客
- **代码review**: 相互学习提升
- **技术培训**: 外部培训,内部分享

**绩效评估**
- **技术能力**: 代码质量,技术深度
- **业务理解**: 需求分析,问题解决
- **协作能力**: 团队合作,沟通能力
- **成长速度**: 学习能力,进步幅度

#### 技术文化建设

**技术价值观**
- **质量优先**: 代码质量,测试覆盖
- **持续学习**: 技术分享,知识沉淀
- **开放协作**: 代码审查,技术讨论
- **勇于创新**: 尝试新技术,改进流程

**技术规范**
- 编码规范: PEP8, Airbnb Style Guide
- Git规范: Commit Message, PR流程
- 文档规范: API文档,设计文档
- 测试规范: 单元测试,集成测试

### 10. 技术决策

#### 决策框架

**决策方法**
- **数据驱动**: 基于性能测试,用户数据
- **成本效益**: 投入产出比分析
- **风险评估**: 潜在风险识别
- **回滚方案**: 失败时如何回退

**决策流程**
1. 问题定义: 明确需要解决的问题
2. 方案调研: 收集多个可行方案
3. 评估分析: 多维度评估方案
4. 小规模验证: PoC验证可行性
5. 决策执行: 实施决策方案
6. 监控反馈: 跟踪实施效果

#### 常见技术决策场景

**单体 vs 微服务**
- 单体: 适合小型团队,快速迭代
- 微服务: 适合大型系统,独立部署

**SQL vs NoSQL**
- SQL: 事务强一致性,结构化数据
- NoSQL: 高并发,灵活schema

**自研 vs 开源**
- 自研: 特殊需求,核心竞争力
- 开源: 成熟稳定,社区支持

**自建 vs 云服务**
- 自建: 成本可控,数据安全
- 云服务: 快速上线,弹性扩展

## 架构文档模板

### 系统架构文档

```markdown
# [系统名称] 架构设计文档

## 1. 概述
### 1.1 系统背景
[描述系统背景和目标]

### 1.2 技术选型
[技术栈说明]

## 2. 架构设计
### 2.1 整体架构
[架构图]

### 2.2 模块设计
[模块划分和职责]

### 2.3 数据设计
[数据模型和存储]

## 3. 关键技术
### 3.1 核心技术
[核心技术说明]

### 3.2 技术难点
[技术难点和解决方案]

## 4. 性能指标
### 4.1 性能目标
[响应时间, 吞吐量等]

### 4.2 监控指标
[监控和告警指标]

## 5. 扩展性设计
### 5.1 水平扩展
[扩展策略]

### 5.2 垂直扩展
[优化方向]

## 6. 安全设计
### 6.1 安全策略
[安全措施]

### 6.2 合规要求
[合规说明]
```

## 使用说明

### 何时使用本技能
- 需要进行系统架构设计
- 需要做技术选型决策
- 需要进行性能优化
- 需要进行代码审查
- 需要制定技术规划
- 需要解决技术难题

### 如何有效使用
1. 提供业务需求和约束条件
2. 说明团队技术背景和限制
3. 明确性能、安全、可靠性要求
4. 提供现有系统信息
5. 保持沟通,及时反馈调整

## 11. SOP引擎架构参考

### 架构设计参考

详见 `assets/sop_architecture_diagram.md`:
- 分层架构设计(API→Func→Core→Utils)
- 数据流架构(提取/分类/验证流程)
- 核心设计模式(抽象基类/混入/DTO/工厂)
- 数据库设计(SOP模板/任务/对话表)
- 性能优化策略(缓存/异步/索引)
- 安全设计(API认证/数据加密)
- 监控和日志(Prometheus/Loguru)
- 扩展性设计(新增分析器/数据源)
- 技术决策记录(ADR文档)

### 关键架构要点

1. **分层架构**: 职责清晰,易于维护
2. **抽象基类**: 统一接口,便于扩展
3. **DTO模式**: 统一状态管理
4. **异步任务**: Redis Streams + Worker
5. **对象存储**: MinIO存储文档和模板
6. **监控完善**: Prometheus + Grafana

## 质量检查清单

在交付架构设计前确认:
- [ ] 架构设计符合业务需求
- [ ] 技术选型有充分依据
- [ ] 性能指标可量化
- [ ] 安全措施完整
- [ ] 可扩展性考虑充分
- [ ] 成本估算合理
- [ ] 风险识别和应对方案
- [ ] 架构文档完整清晰
