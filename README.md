# 旋转目标检测标注格式转换工具

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个用于旋转目标检测任务的标注格式转换工具，支持在 **RoLabelImg (类VOC XML)** 格式和 **DOTA (TXT)** 格式之间进行双向、批量的转换。

---

## 📋 支持的格式

### 1. RoLabelImg 格式 (输入/输出)
一种基于 XML 的标注格式，通过中心点、宽高和旋转角度（弧度制）来定义旋转框。

**示例 (`.xml`):**
```xml
<annotation>
    <filename>P0001.jpg</filename>
    <size>
        <width>1024</width>
        <height>1024</height>
        <depth>3</depth>
    </size>
    <object>
        <name>ship</name>
        <difficult>0</difficult>
        <robndbox>
            <cx>500.0</cx>
            <cy>300.0</cy>
            <w>100.0</w>
            <h>50.0</h>
            <angle>0.7854</angle>
        </robndbox>
    </object>
</annotation>
```

### 2. DOTA 格式 (输入/输出)
一种基于文本的标注格式，通过旋转框的四个顶点坐标来定义。

**示例 (`.txt`):**
```plaintext
x1 y1 x2 y2 x3 y3 x4 y4 classname difficult
314.6 289.6 379.3 325.0 353.9 350.4 289.3 315.0 ship 0
```

---

## 🛠️ 安装

1.  **克隆项目**
    ```bash
    git clone [https://github.com/SeanWong17/Rotated-Annotation-Converter.git](https://github.com/SeanWong17/Rotated-Annotation-Converter.git)
    cd Rotated-Annotation-Converter
    ```

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

---

## 📖 使用方法

本工具提供了一个统一的命令行接口，支持两种转换模式。

### 1. RoLabelImg → DOTA

将一个文件夹内所有的 RoLabelImg XML 文件批量转换为 DOTA TXT 文件。

**命令格式:**
```bash
python main.py ro2dota --xml-dir <输入XML文件夹> --txt-dir <输出TXT文件夹>
```

**示例:**
```bash
python main.py ro2dota --xml-dir ./rolabelimg_annotations --txt-dir ./dota_annotations
```

### 2. DOTA → RoLabelImg

将一个文件夹内所有的 DOTA TXT 文件批量转换为 RoLabelImg XML 文件。

**注意:** 此转换需要提供对应的原始图片文件夹，以便程序获取每张图片的宽高信息并写入XML。

**命令格式:**
```bash
python main.py dota2ro --txt-dir <输入TXT文件夹> --img-dir <原始图片文件夹> --xml-dir <输出XML文件夹>
```

**示例:**
```bash
python main.py dota2ro --txt-dir ./dota_annotations --img-dir ./images --xml-dir ./rolabelimg_annotations
```

---

## 🔬 转换原理

* **RoLabelImg → DOTA**: 基于中心点 `(cx, cy)`、宽高 `(w, h)` 和旋转角度 `angle`，通过旋转矩阵计算出未旋转时框的四个顶点，再将这些顶点围绕中心点旋转 `angle` 角度，得到最终的四点坐标。
* **DOTA → RoLabelImg**: 基于四点坐标 `(x1, y1)...(x4, y4)`，通过几何关系计算出矩形的中心点（对角线交点）、宽高（邻边距离）以及由边向量与x轴计算出的旋转角度。

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。
