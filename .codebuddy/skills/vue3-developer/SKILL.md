---
name: Vue3前端开发工程师
description: 专业的Vue3前端开发专家,精通Vue3全家桶(Vue3 + Vite + Pinia + Vue Router),能够构建现代化Web应用。适用于组件开发、页面搭建、状态管理、路由设计、性能优化等前端开发场景。
---

# Vue3前端开发工程师技能

## 概述

本技能提供专业的Vue3前端开发能力,涵盖从组件设计到完整应用构建的全流程。帮助快速构建高性能、可维护的Vue3应用。

## 技术栈

### 核心技术
- **Vue 3**: Composition API、响应式系统、生命周期
- **Vite**: 构建工具、开发服务器
- **Pinia**: 状态管理
- **Vue Router**: 路由管理
- **TypeScript**: 类型支持

### 常用生态
- **UI框架**: Element Plus、Ant Design Vue、Naive UI
- **CSS方案**: Tailwind CSS、UnoCSS、SCSS/Less
- **请求库**: Axios、Fetch API
- **工具库**: Lodash-es、Day.js

## 核心能力

### 1. Vue3 Composition API开发

#### 组合式函数(Composables)
使用Composition API编写可复用的逻辑:

```javascript
// 基础composable示例
import { ref, computed, onMounted } from 'vue'

export function useCounter(initialValue = 0) {
  const count = ref(initialValue)
  
  const increment = () => count.value++
  const decrement = () => count.value--
  const double = computed(() => count.value * 2)
  
  return {
    count,
    increment,
    decrement,
    double
  }
}
```

#### 响应式系统
- `ref()`: 基本类型响应式
- `reactive()`: 对象响应式
- `computed()`: 计算属性
- `watch() / watchEffect()`: 监听变化
- `toRefs()`: 解构响应式对象

### 2. 组件设计与开发

#### 组件结构规范
```vue
<script setup lang="ts">
// 1. 导入
import { ref, computed } from 'vue'
import type { PropType } from 'vue'

// 2. Props定义
interface Props {
  title: string
  items?: Array<{ id: number; name: string }>
}

const props = defineProps<Props>()

// 3. Emits定义
const emit = defineEmits<{
  update: [value: string]
  delete: [id: number]
}>()

// 4. 响应式状态
const isVisible = ref(false)

// 5. 计算属性
const filteredItems = computed(() => 
  props.items?.filter(item => item.name.includes('test')) || []
)

// 6. 方法
const handleClick = () => {
  emit('update', 'new value')
}
</script>

<template>
  <div class="my-component">
    <h2>{{ title }}</h2>
    <ul>
      <li v-for="item in filteredItems" :key="item.id">
        {{ item.name }}
      </li>
    </ul>
  </div>
</template>

<style scoped lang="scss">
.my-component {
  padding: 16px;
}
</style>
```

#### 组件设计原则
- **单一职责**: 每个组件只做一件事
- **可复用性**: 通过Props和插槽增强灵活性
- **性能优先**: 合理使用`v-if`/`v-show`、`computed`、`key`
- **类型安全**: 使用TypeScript定义Props和Emits

### 3. 状态管理(Pinia)

#### Store定义
```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string>('')
  
  // Getters
  const isLoggedIn = computed(() => !!token.value)
  
  // Actions
  const login = async (credentials: LoginCredentials) => {
    const response = await api.login(credentials)
    user.value = response.user
    token.value = response.token
  }
  
  const logout = () => {
    user.value = null
    token.value = ''
  }
  
  return {
    user,
    token,
    isLoggedIn,
    login,
    logout
  }
})
```

#### Store使用最佳实践
- 使用`setup`语法定义Store
- 将State、Getters、Actions分离清晰
- 使用TypeScript确保类型安全
- 合理拆分Store,避免过度集中

### 4. 路由管理(Vue Router)

#### 路由配置
```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/user/:id',
    name: 'UserDetail',
    component: () => import('@/views/UserDetail.vue'),
    props: true
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/AdminView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const { requiresAuth } = to.meta
  const userStore = useUserStore()
  
  if (requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
```

#### 路由最佳实践
- 使用路由懒加载提升性能
- 通过meta配置路由元信息
- 合理使用路由守卫进行权限控制
- 命名路由和命名视图提升可维护性

### 5. API请求封装

#### Axios封装
```typescript
// utils/request.ts
import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import { useUserStore } from '@/stores/user'

const instance: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
instance.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default instance
```

### 6. 性能优化

#### 代码层面优化
- 使用`v-once`渲染静态内容
- 合理使用`computed`缓存计算结果
- 避免不必要的响应式数据
- 使用`v-memo`缓存列表项
- 懒加载组件和路由

#### 构建优化
- 配置Vite的代码分割策略
- 使用Tree-shaking去除无用代码
- 开启Gzip压缩
- 图片资源优化和懒加载

#### 运行时优化
- 虚拟滚动处理长列表
- 防抖和节流处理高频事件
- 使用`requestIdleCallback`延迟非关键任务
- 合理使用`keep-alive`缓存组件

### 7. 常用UI组件库集成

#### Element Plus
```typescript
// main.ts
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

app.use(ElementPlus, { locale: zhCn })
```

#### Ant Design Vue
```typescript
// main.ts
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'

app.use(Antd)
```

## 项目结构推荐

```
src/
├── api/              # API接口
├── assets/           # 静态资源
├── components/       # 公共组件
│   ├── common/       # 通用组件
│   └── business/     # 业务组件
├── composables/      # 组合式函数
├── layouts/          # 布局组件
├── router/           # 路由配置
├── stores/           # Pinia状态管理
├── styles/           # 全局样式
├── types/            # TypeScript类型定义
├── utils/            # 工具函数
├── views/            # 页面组件
└── App.vue
```

## 代码规范

### 命名规范
- **组件**: PascalCase (e.g., `UserProfile.vue`)
- **文件**: kebab-case (e.g., `user-profile.ts`)
- **变量/函数**: camelCase (e.g., `getUserInfo`)
- **常量**: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- **接口/类型**: PascalCase (e.g., `User`)

### Vue风格指南
遵循Vue官方风格指南:
- 使用Composition API语法`<script setup>`
- Props定义使用TypeScript类型
- 优先使用`v-for`的`:key`
- 避免`v-if`和`v-for`在同一元素使用
- 组件名使用多单词

### TypeScript最佳实践
- 严格开启`strict: true`
- 优先使用`interface`定义对象类型
- 使用泛型提升代码复用性
- 避免使用`any`,使用`unknown`替代

## 常见问题处理

### 响应式失效
- 确保使用`ref`或`reactive`包装数据
- 解构时使用`toRefs()`
- 直接修改数组索引时使用`Vue.set`或`splice`

### 组件通信
- Props down, Events up
- 跨组件通信使用Provide/Inject
- 全局状态使用Pinia
- 复杂场景考虑事件总线或状态机

### 类型错误
- 使用`defineProps<T>()`定义Props类型
- 使用`defineEmits<T>()`定义Emits类型
- 为组件Props定义明确的接口

## 调试技巧

### Vue DevTools
- 安装Vue DevTools浏览器插件
- 查看组件树、Props、State
- 追踪事件触发和路由变化
- 性能分析Pinia状态变化

### 控制台调试
```typescript
// 开发环境打印调试信息
if (import.meta.env.DEV) {
  console.log('Debug info:', data)
}
```

## 使用说明

### 何时使用本技能
- 需要开发Vue3组件或页面
- 需要设计前端架构和状态管理
- 需要优化Vue应用性能
- 需要集成第三方UI组件库
- 需要处理前端工程化配置

### 如何有效使用
1. 明确需求和技术选型
2. 确定UI框架和样式方案
3. 提供接口文档或Mock数据
4. 说明设计规范和交互要求
5. 保持沟通,及时反馈调整

## 质量检查清单

在交付代码前确认:
- [ ] 代码符合Vue3 Composition API最佳实践
- [ ] TypeScript类型定义完整
- [ ] 组件职责单一,可复用性良好
- [ ] Props和Emits类型明确
- [ ] 状态管理逻辑合理
- [ ] 性能优化措施到位
- [ ] 代码注释清晰可读
- [ ] 没有控制台错误或警告

## 8. SOP引擎前端集成

### 8.1 API接口集成

```typescript
// api/sop.ts
import request from '@/utils/request'
import type { SOPTemplate, ValidationRequest, ValidationResponse } from '@/types/sop'

// 获取SOP模板列表
export const getSOPTemplates = () => {
  return request.get<SOPTemplate[]>('/api/v1/sop/templates')
}

// 获取SOP模板详情
export const getSOPTemplate = (templateId: string) => {
  return request.get<SOPTemplate>(`/api/v1/sop/templates/${templateId}`)
}

// 提交验证任务
export const validateConversation = (data: ValidationRequest) => {
  return request.post<ValidationResponse>('/api/v1/sop/validate', data)
}

// 上传文档
export const uploadDocument = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<{ extraction_id: string }>('/api/v1/sop/extract', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
```

### 8.2 状态管理

```typescript
// stores/sop.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { SOPTemplate } from '@/types/sop'

export const useSOPStore = defineStore('sop', () => {
  // State
  const templates = ref<SOPTemplate[]>([])
  const currentTemplate = ref<SOPTemplate | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const templateOptions = computed(() =>
    templates.value.map(t => ({
      label: t.template_name,
      value: t.sop_template_id
    }))
  )

  // Actions
  const fetchTemplates = async () => {
    loading.value = true
    error.value = null
    try {
      templates.value = await getSOPTemplates()
    } catch (err: any) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  const selectTemplate = async (templateId: string) => {
    currentTemplate.value = await getSOPTemplate(templateId)
  }

  return {
    templates,
    currentTemplate,
    loading,
    error,
    templateOptions,
    fetchTemplates,
    selectTemplate
  }
})
```

### 8.3 组件示例

```vue
<!-- components/SOPValidator.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { validateConversation } from '@/api/sop'
import { useSOPStore } from '@/stores/sop'

const sopStore = useSOPStore()

const form = ref({
  conversation_id: '',
  conversation_json_path: '',
  sop_template_id: ''
})

const loading = ref(false)

const handleValidate = async () => {
  loading.value = true
  try {
    const result = await validateConversation(form.value)
    ElMessage.success('验证任务已提交')
    // 处理结果
  } catch (error: any) {
    ElMessage.error(error.message || '验证失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-card title="SOP验证">
    <el-form :model="form" label-width="120px">
      <el-form-item label="SOP模板">
        <el-select
          v-model="form.sop_template_id"
          placeholder="请选择SOP模板"
        >
          <el-option
            v-for="option in sopStore.templateOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleValidate"
        >
          开始验证
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>
```

### 8.4 类型定义

```typescript
// types/sop.ts
export interface SOPTemplate {
  sop_template_id: string
  template_name: string
  product_type: string
  product_subtype: string
  description: string
  risk_level: string
  structure: {
    node_id: string
    name: string
    children: any[]
  }
  detection_rules: {
    completeness_weight: number
    sequence_weight: number
    quality_weight: number
    pass_score: number
  }
  version: string
  status: 'active' | 'inactive'
}

export interface ValidationRequest {
  conversation_id: string
  conversation_json_path: string
  sop_template_id: string
  enable_taboo_detection?: boolean
  enable_sensitive_detection?: boolean
}

export interface ValidationResponse {
  validation_id: string
  status: 'processing' | 'completed' | 'failed'
  result_json_path?: string
  processing_time?: number
}
```
