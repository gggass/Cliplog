# Cliplog 架构

## 整体思路

Python 做主控，每隔 1 秒启动一次 C++ 小程序（clip.exe）抓剪切板文本，然后比对去重，写入 records/ 目录下的 JSONL 文件。

C++ 程序无状态，用完即退，不常驻。这样做的好处是不需要 Windows 消息循环，架构简单。

## 线程模型

GUI 在主线程跑 tkinter mainloop，监控循环在 daemon 线程跑。两个线程共享 ClipboardMonitor 对象，通过 `threading.Event()` 通信——Start 清零，Stop 置位。daemon=True 意味着主线程退出时守护线程自动跟着结束，不用手动管生命周期。

## 各模块干什么

**clip.cpp** — 从 Windows 剪切板拿文本，打印到 stdout，退出。依赖 user32.dll 的 Clipboard API。运行时长不到 1ms。

**cliplog.py** — GUI 界面、定时调度、去重、记录管理。常驻进程，点 Stop 或关窗口退出。依赖 tkinter、threading、subprocess。

## 数据流

剪切板 UTF-16 文本 → clip.cpp 通过 OpenClipboard/GetClipboardData/GlobalLock 拿到 → 转成 UTF-8 输出到 stdout → Python subprocess 读到 → 和上次内容比对 → 变了就写一条到 records/YYYY-MM-DD.jsonl

## 存储格式

按天分文件，每行一条 JSON：

```json
{"time": "2026-05-27T14:32:05+08:00", "text": "...", "length": 123}
```

## 文件结构

```
Cliplog/
├── clip.cpp
├── cliplog.py
├── records/          # 记录文件
├── .gitignore
└── ARCHITECTURE.md
```
