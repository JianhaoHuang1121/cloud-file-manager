# 雲端檔案管理系統

應用 Composite Pattern 設計的雲端檔案管理系統。

## 功能

### 必要功能
- 目錄結構顯示（樹狀格式）
- 遞迴計算總容量
- 副檔名搜尋
- XML 結構輸出
- Traverse Log（演算法執行紀錄）

### 加分功能
- 排序（依名稱 / 大小 / 副檔名，可升降冪）
- 刪除節點
- 複製貼上
- 多重標籤（Urgent / Work / Personal）
- Undo / Redo（基於 Command Pattern）

## 設計概述

### Composite Pattern
本系統的核心設計。`Directory` 與各類 `File`(WordFile / ImageFile / TextFile) 共同繼承抽象基底類別 `FileSystemNode`。透過統一介面，目錄與檔案可以用相同的方式操作（顯示、計算大小、搜尋），而 `Directory.children` 中可以放入任何 `FileSystemNode` 子類，讓樹狀結構可以無限套疊。

### 演算法
計算容量與副檔名搜尋皆採用 DFS（深度優先搜尋）遞迴遍歷。每個 `Directory` 節點會將自己的 `get_size()` 或 `search()` 委派給所有子節點，逐層往下走訪到葉節點再向上加總或彙整結果。

### Command Pattern
為支援 Undo / Redo，每一個操作（新增、刪除、複製）都被封裝成 `Command` 物件，內含 `execute()` 與 `undo()` 方法。`CommandHistory` 透過兩個 stack 管理歷史與重做佇列，執行新命令時清空 redo stack（與一般文書編輯器行為一致）。

## 資料庫設計（ER Model）

採用 Table Per Hierarchy（單表繼承）設計：
- `file_system_node`：所有節點共用欄位，`parent_id` 自我參照形成樹狀結構
- `word_file` / `image_file` / `text_file`：各類型專屬欄位
- `node_tag`：標籤關聯表（支援多重標籤）

## 環境需求
- Python 3.10+
- 僅使用標準函式庫（無額外相依套件）

## 執行方式
```
python main.py
```
