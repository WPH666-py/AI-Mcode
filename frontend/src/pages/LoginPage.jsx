import React, { useState } from 'react'
import { Card, Form, Input, Button, App, Tabs, Typography } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons'
import api from '../api'

const { Text } = Typography

export default function LoginPage({ onLogin }) {
  const { message } = App.useApp()
  const [loading, setLoading] = useState(false)

  const handleLogin = async (values) => {
    setLoading(true)
    try {
      const res = await api.post('/auth/token/', {
        username: values.username,
        password: values.password,
      })
      localStorage.setItem('access_token', res.data.access)
      localStorage.setItem('refresh_token', res.data.refresh)
      onLogin()
    } catch (e) {
      message.error('登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (values) => {
    setLoading(true)
    try {
      await api.post('/auth/register/', {
        username: values.username,
        password: values.password,
        email: values.email || '',
      })
      message.success('注册成功，请登录')
    } catch (e) {
      const errMsg = e.response?.data?.detail || e.response?.data?.username?.[0] || '注册失败'
      message.error(errMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <section className="login-hero">
        <div className="login-brand">M</div>
        <h1>面向本地工作的数学建模 AI 工作台</h1>
        <p>
          集成题目解析、数据处理、建模推导、代码生成与运行反馈，帮助你以更清晰的流程完成数学建模任务。
        </p>
      </section>

      <section className="login-panel-wrap">
        <Card className="login-card" variant="borderless">
          <div className="login-title">欢迎使用</div>
          <Text className="login-subtitle">登录后进入你的本地建模项目空间</Text>

          <Tabs
            centered
            size="large"
            items={[
              {
                key: 'login',
                label: '登录',
                children: (
                  <Form className="professional-form" onFinish={handleLogin} size="large" layout="vertical">
                    <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}> 
                      <Input prefix={<UserOutlined />} placeholder="用户名" />
                    </Form.Item>
                    <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}> 
                      <Input.Password prefix={<LockOutlined />} placeholder="密码" />
                    </Form.Item>
                    <Form.Item style={{ marginTop: 26, marginBottom: 0 }}>
                      <Button type="primary" htmlType="submit" loading={loading} block size="large">
                        登录
                      </Button>
                    </Form.Item>
                  </Form>
                ),
              },
              {
                key: 'register',
                label: '注册',
                children: (
                  <Form className="professional-form" onFinish={handleRegister} size="large" layout="vertical">
                    <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}> 
                      <Input prefix={<UserOutlined />} placeholder="用户名" />
                    </Form.Item>
                    <Form.Item name="email">
                      <Input prefix={<MailOutlined />} placeholder="邮箱（可选）" />
                    </Form.Item>
                    <Form.Item name="password" rules={[{ required: true, min: 6, message: '密码至少6位' }]}> 
                      <Input.Password prefix={<LockOutlined />} placeholder="密码" />
                    </Form.Item>
                    <Form.Item style={{ marginTop: 26, marginBottom: 0 }}>
                      <Button type="primary" htmlType="submit" loading={loading} block size="large">
                        注册
                      </Button>
                    </Form.Item>
                  </Form>
                ),
              },
            ]}
          />
        </Card>
      </section>
    </div>
  )
}
