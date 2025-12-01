# Warm-up Task: Web Builder with PaddleOCR & ERNIE

## 任务说明

使用 PaddleOCR-VL 从 PDF 提取文本和布局，转换为 Markdown，然后使用 ERNIE 模型生成网页，最后部署到 GitHub Pages。

## 工作流程

```
PDF文档 → PaddleOCR-VL提取 → Markdown → ERNIE生成HTML → GitHub Pages部署
```

## 使用方法

### 1. 安装依赖

```bash
cd DocuMind
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 ERNIE API Key
```

### 3. 运行转换脚本

```bash
cd warmup_task
python pdf_to_web.py your_document.pdf output.html
```

### 4. 部署到 GitHub Pages

```bash
# 将生成的HTML复制到docs目录
cp output.html ../docs/index.html

# 提交到GitHub
git add .
git commit -m "Add generated web page"
git push

# 在GitHub仓库设置中启用Pages，选择docs目录
```

## 示例输出

生成的网页包含：
- 响应式设计
- 现代化CSS样式
- 从PDF提取的完整内容
- DocuMind品牌标识

## 技术实现

1. **PaddleOCR-VL**: 高精度OCR识别，支持复杂布局
2. **Markdown转换**: 保留文档结构
3. **ERNIE生成**: 智能生成美观的HTML页面
4. **GitHub Pages**: 免费静态网站托管

## 文件说明

- `pdf_to_web.py` - 主转换脚本
- `sample_output.html` - 示例输出
