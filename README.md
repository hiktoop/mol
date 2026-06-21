# mol — 我的 OPDS 书库

私人电子书 OPDS 目录，配合 [Readest](https://readest.com) 或任意支持 OPDS 的阅读器使用。

## OPDS 地址

```
https://hiktoop.github.io/mol/catalog.xml
```

在 Readest 里：Library → Online Library → 粘贴上面的 URL

---

## 添加新书

### 1. 上传书籍文件

在 GitHub 仓库创建一个新 Release（或复用已有 Release），把 `.epub` / `.pdf` 作为 asset 上传，复制文件的直链地址（格式：`https://github.com/hiktoop/mol/releases/download/TAG/file.epub`）。

### 2. 添加书目 JSON

在 `books/` 目录新建一个 `书名id.json`，参照现有格式填写，把上一步的下载链接填入 `download_url`。

### 3. 推送

```bash
git add .
git commit -m "add: 书名"
git push
```

GitHub Actions 自动运行，几十秒后 `catalog.xml` 更新。

---

## 目录结构

```
mol/
├── books/              # 书目元数据（JSON，不放书籍文件本身）
├── covers/             # 封面图（可选，jpg/png）
├── generate_catalog.py # 生成 catalog.xml 的脚本
└── .github/workflows/
    └── deploy.yml      # 自动部署到 gh-pages
```

---

## 本地预览

```bash
python generate_catalog.py
# 生成 catalog.xml，可用浏览器或 curl 查看
```
