# Anaconda 环境配置指南

若在终端执行 `python` 提示找不到命令，可将 Anaconda 添加到系统 PATH，使任意终端（CMD、PowerShell、VS Code 等）执行 `python` 时自动使用 Anaconda。

## 一、添加 Anaconda 到 PATH（推荐）

### 方法 A：一键脚本（如项目提供）

1. 进入项目 `scripts` 文件夹（若存在）
2. **右键** `添加Anaconda到系统PATH-以管理员运行.bat` → **以管理员身份运行**
3. 在弹出的 UAC 提示中点击 **是**
4. 脚本执行完成后，**关闭并重新打开**所有终端
5. 在任意终端执行 `python` 验证

### 方法 B：通过系统环境变量（手动）

1. 按 `Win + R`，输入 `sysdm.cpl`，回车
2. 点击 **高级** → **环境变量**
3. 在 **用户变量** 或 **系统变量** 中选中 `Path`，点击 **编辑**
4. 点击 **新建**，依次添加：
   ```
   C:\ProgramData\anaconda3
   C:\ProgramData\anaconda3\Scripts
   C:\ProgramData\anaconda3\Library\bin
   ```
5. 确定保存，**重新打开**终端后再试 `python`

> 若 Anaconda 装在用户目录，路径可能为 `C:\Users\你的用户名\anaconda3`

### 方法 C：使用 Anaconda Prompt（临时）

1. 从开始菜单打开 **Anaconda Prompt**
2. 在 Anaconda Prompt 中执行：
   ```cmd
   cd /d d:\研发项目123\数据要素\DataHealthCheck\backend
   .\start.ps1
   ```
   若 PowerShell 脚本无法执行，可改为：
   ```cmd
   python -m app.db.init_db
   python seed_data.py
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

## 二、启动后端

将 Anaconda 添加到 PATH 后，在 `backend` 目录下执行：

**PowerShell**：
```powershell
.\start.ps1
```

**或手动执行**：
```cmd
python -m app.db.init_db
python seed_data.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 三、验证

在任意终端执行：

```cmd
python --version
```

能输出版本号即表示配置成功。
