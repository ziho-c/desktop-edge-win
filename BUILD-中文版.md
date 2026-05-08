# Ziti Desktop Edge for Windows - 中文版构建说明

> 已经在源码里把 198 处英文文案改成中文（XAML + C# 字面量直接覆盖）。
> 这份指南教你**在一台 Windows 机器上把它编译成 .exe**。

---

## 你需要准备

在一台 Windows 10/11 电脑上：

1. **Visual Studio 2022 Community**（免费）
   - 下载：https://visualstudio.microsoft.com/zh-hans/vs/community/
   - 安装时勾选 **".NET 桌面开发"** 工作负载
   - 也勾上 **".NET Framework 4.8 目标包"**（在右侧"安装详细信息"里）

2. **NuGet CLI**
   - 下载 nuget.exe：https://www.nuget.org/downloads（取 "Latest recommended" 那个 .exe）
   - 把 `nuget.exe` 放进 `C:\Tools\` 或任何在 PATH 里的目录

3. **PowerShell 7+**（一般 Win11 自带，Win10 可能要装）
   - 检查：`pwsh --version`
   - 没有的话：`winget install --id Microsoft.PowerShell`

> 不需要 Advanced Installer 等付费工具 —— 那个只是用来打 .msi 安装包，我们直接用编出来的 `.exe` 就行。

---

## 解压源码

把我给你的 `zdew-zh-src.tgz` 在 Windows 上用 7-Zip 解压（或者在 PowerShell：`tar -xzf zdew-zh-src.tgz`），得到 `desktop-edge-win-zh\` 文件夹。

```
desktop-edge-win-zh/
├── DesktopEdge/                   ← 主 UI 工程（已中文化）
├── ZitiUpdateService/             ← Update Service
├── ZitiDesktopEdge.sln            ← Visual Studio 解决方案
├── scripts/
│   ├── extract-strings.py         ← 提取 UI 字符串的脚本
│   ├── translations.json          ← 翻译表（要再翻就改这个）
│   └── translate-zh.py            ← 应用翻译的脚本
└── BUILD-中文版.md                ← 本文档
```

---

## 编译

打开 **"Developer PowerShell for VS 2022"**（在开始菜单搜索）—— 这个 PowerShell 已经把 `msbuild` 加到 PATH 了。

```powershell
cd C:\path\to\desktop-edge-win-zh
nuget restore ZitiDesktopEdge.sln
msbuild ZitiDesktopEdge.sln /p:Configuration=Release
```

第一次 `nuget restore` 大概 1-3 分钟，`msbuild` 5-10 分钟。

**编出来的 exe 在**：
```
DesktopEdge\bin\Release\ZitiDesktopEdge.exe
```

直接双击运行就是中文版。

---

## 装到员工电脑上

**最朴素的做法**（适合 IT 团队 50 人）：

1. 在编出来的 `Release\` 目录下把所有文件 zip 起来（`ZitiDesktopEdge.exe` + 一堆 `.dll`）
2. 发给员工：解压到某目录，例如 `C:\Program Files\ZitiZH\`
3. 双击 `ZitiDesktopEdge.exe` 运行

> 注意：这种朴素方式**没有反卸载、没有自启动、没有数字签名**。SmartScreen 第一次会拦截，要选"仍要运行"。
> 如果要"开机自启 + 后台保活 + 数字签名"，就需要再装 Advanced Installer 打 .msi 了。但这都是商业产品才需要的体验，你们 IT 兜底用不需要。

---

## 装好后怎么 enroll

跟原版一样：

1. 我给你的 `.jwt` 文件（之前 add-user.sh 生成的那种）
2. 在客户端里 **Add Identity → From File** → 选 `.jwt` 文件
3. enroll 完成，永久免登录

---

## 想再翻更多文案怎么办

**找到漏翻的字符串**：
1. 装好客户端，打开界面，截图告诉我哪里还是英文
2. 或者直接编辑 `scripts/translations.json` 加一条 `"英文": "中文"`

**重跑翻译 + 重 build**：
```powershell
# 重跑翻译（需要 Python 3）
cd desktop-edge-win-zh
python scripts/translate-zh.py

# 清除旧编译产物
msbuild ZitiDesktopEdge.sln /t:Clean /p:Configuration=Release

# 重新编译
msbuild ZitiDesktopEdge.sln /p:Configuration=Release
```

---

## 已翻范围（约 200 条）

- 主窗口、菜单、标签页、按钮（保存/取消/关闭/刷新/重置等）
- Identity 管理（添加、移除、详情、Provider 选择）
- MFA 流程、JWT/Url 入网流程
- 错误提示、状态文本（连接/已启用/未启用/加载中等）
- 网络配置（DNS/IP/端口/协议等技术词保留缩写）

## 不翻的部分

- 第三方库的 UI（极少）
- 动态从后端拼接的字符串（取决于 controller 返回什么）
- 日志输出（开发者看的，无需翻译）
- 字体名（"Segoe UI"）、DLL 名（"Kernel32.dll"）等技术标识

---

## 如果编译报错

| 错误 | 解决 |
|---|---|
| `MSB4025` / `Could not load file` | 先跑 `nuget restore` |
| `error MSB4019: 无法导入...Microsoft.NET.Sdk.WindowsDesktop` | VS 安装时漏勾".NET 桌面开发"，重装 VS Installer 修复 |
| `CSx 找不到类型...` | 缺 .NET Framework 4.8 SDK，VS Installer 里勾上 |
| 中文显示乱码 | 你的 PowerShell 编码不是 UTF-8，运行 `$OutputEncoding = [console]::OutputEncoding = [Text.UTF8Encoding]::UTF8` |
| 编出来的 exe 显示英文 | 翻译没生效。先在源码里 `grep -r '保存' DesktopEdge\` 看是否有中文字符；如果没有，手动跑 `python scripts/translate-zh.py` |

---

## 把 .exe 给我看效果

编完后压缩 `Release\` 目录发我（或者你自己装上看），我看哪里还是英文，再补 `translations.json`。
