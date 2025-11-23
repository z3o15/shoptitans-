# GitHub 提交指南

本指南将帮助您将游戏装备图像识别系统提交到GitHub仓库。

## 前置准备

在开始之前，请确保您已经：
1. 安装了Git
2. 创建了GitHub账户
3. 在GitHub上创建了新仓库（或准备推送到现有仓库）

## 提交步骤

### 1. 初始化本地Git仓库

如果您的项目还没有初始化Git仓库，请在项目根目录执行：

```bash
git init
```

### 2. 添加远程仓库

将您的GitHub仓库添加为远程仓库（替换`YOUR_USERNAME`和`YOUR_REPO_NAME`）：

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### 3. 配置Git用户信息（首次使用）

```bash
git config --global user.name "您的姓名"
git config --global user.email "您的邮箱@example.com"
```

### 4. 添加文件到暂存区

```bash
git add .
```

### 5. 提交文件

```bash
git commit -m "Initial commit: 游戏装备图像识别系统

- 实现基于多重算法的装备识别功能
- 支持特征匹配、高级模板匹配和传统dHash算法
- 添加OCR金额识别功能
- 实现四步工作流程：获取截图→分割图片→装备匹配→整合结果
- 添加完整的配置管理系统
- 提供增强版和基础版启动脚本"
```

### 6. 推送到GitHub

```bash
git branch -M main
git push -u origin main
```

## 完整命令序列

以下是完整的命令序列，您可以一次性执行：

```bash
# 初始化仓库
git init

# 添加远程仓库（请替换为您的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 添加所有文件
git add .

# 提交文件
git commit -m "Initial commit: 游戏装备图像识别系统

- 实现基于多重算法的装备识别功能
- 支持特征匹配、高级模板匹配和传统dHash算法
- 添加OCR金额识别功能
- 实现四步工作流程：获取截图→分割图片→装备匹配→整合结果
- 添加完整的配置管理系统
- 提供增强版和基础版启动脚本"

# 推送到GitHub
git branch -M main
git push -u origin main
```

## 注意事项

1. **仓库地址**：请确保将`YOUR_USERNAME`和`YOUR_REPO_NAME`替换为您的实际GitHub用户名和仓库名称。

2. **私有仓库**：如果您想创建私有仓库，可以在GitHub上创建时选择"Private"选项，或者使用以下命令：
   ```bash
   git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
   ```

3. **大文件处理**：如果您的项目包含大文件（如大型图像文件），可能需要使用Git LFS（Large File Storage）。

4. **分支管理**：如果您想使用不同的分支名称，可以修改`main`为您想要的分支名称。

## 后续维护

提交完成后，您可以：

1. 在GitHub上查看您的代码
2. 创建Release版本
3. 添加Wiki文档
4. 设置Issues和Pull Requests

## 常见问题

**Q: 推送时提示身份验证错误？**
A: 请确保您已正确配置GitHub的SSH密钥或使用HTTPS进行身份验证。

**Q: 提示"remote origin already exists"？**
A: 表示已经配置了远程仓库，可以使用`git remote -v`查看现有远程仓库。

**Q: 如何忽略某些文件？**
A: 项目已包含`.gitignore`文件，会自动忽略不需要的文件。

---

完成这些步骤后，您的游戏装备图像识别系统就成功提交到GitHub了！