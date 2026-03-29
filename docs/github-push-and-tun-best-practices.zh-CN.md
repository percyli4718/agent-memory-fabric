# GitHub Push 与 TUN 代理最佳实践

## 背景

在本机环境中，已经验证出 `v2rayN` 的 `TUN` 模式会影响 GitHub 的 SSH 推送，而关闭 `TUN` 后推送可以恢复正常。

本次实际现象如下：

- `TUN` 开启时：
  - `ssh -T git@github.com` 可能出现连接被关闭
  - `git push` 可能出现 `Connection closed by ... port 443`
- `TUN` 关闭时：
  - `ssh -T git@github.com` 可以成功认证
  - `git push -u origin main` 可以成功推送

这说明当前机器上的主要影响因素是：

- `v2rayN` 的 `TUN/透明代理` 会干扰 `SSH over 443`
- 普通全局代理未必是问题核心

## 当前仓库配置

当前仓库远程采用 SSH：

```bash
git@github.com:percyli4718/agent-memory-fabric.git
```

当前 SSH 配置建议为：

```sshconfig
Host github.com
  HostName ssh.github.com
  Port 443
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

## 推荐操作流程

### 日常回答问题

如果 Codex 或当前工作流依赖 `TUN` 模式保持网络稳定，可以在正常开发和提问时维持当前代理配置。

### 推送 GitHub 时

在执行 GitHub 的 `push`、`pull`、`fetch`、`clone` 等 SSH 操作前，建议：

1. 临时关闭 `v2rayN` 的 `TUN` 模式
2. 保留普通代理或全局代理设置
3. 执行 Git 命令
4. 操作完成后再恢复 `TUN`

示例：

```bash
git -C /home/sanding/workspace/openProject/agent-memory-fabric push -u origin main
```

## 建议排查命令

### 检查 SSH 认证

```bash
ssh -T git@github.com
```

成功时常见输出：

```text
Hi percyli4718! You've successfully authenticated, but GitHub does not provide shell access.
```

### 检查远程地址

```bash
git -C /home/sanding/workspace/openProject/agent-memory-fabric remote -v
```

### 检查当前 SSH key 是否已加载

```bash
ssh-add -l
```

## 故障判断经验

### 现象 1

```text
Connection closed by ... port 443
```

更偏向于：

- `TUN` 或透明代理链路干扰
- 网络中间路径重置 SSH 会话

### 现象 2

```text
Permission denied (publickey)
```

更偏向于：

- GitHub 上未添加公钥
- `ssh-agent` 未加载私钥
- `~/.ssh/config` 未命中正确 key

## 最佳实践建议

1. GitHub 的 SSH 推送优先使用 `ssh.github.com:443`
2. 将 `github.com` 的 SSH 流量尽量排除出 `TUN` 干扰路径
3. 推送前先用 `ssh -T git@github.com` 做一次快速验证
4. 重要版本推送前，先确认：
   - 工作树干净
   - 测试通过
   - commit 信息规范
5. 如果未来仍频繁被 `TUN` 干扰，可以考虑为 GitHub 单独做分流规则

## 适用于本项目的版本发布习惯

建议项目发布时遵循：

1. 先本地开发与测试
2. 再做代码审查式自查
3. 再提交 commit
4. 推送前临时关闭 `TUN`
5. 推送成功后记录版本结果

## 备注

当前项目已经确认：

- 关闭 `TUN` 后，`main` 分支可以成功推送到 GitHub
- 因此后续版本迭代可以继续保持：
  - 开发时按当前网络习惯工作
  - 推送时临时关闭 `TUN`
