import os
import math
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from typing import List, Tuple, Dict
from PIL import Image

# --- 数学与几何计算函数 ---

def _rotate_point(xc: float, yc: float, xp: float, yp: float, theta: float) -> Tuple[float, float]:
    """围绕中心点旋转一个点 (私有函数)"""
    xoff = xp - xc
    yoff = yp - yc
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    p_resx = cos_theta * xoff + sin_theta * yoff
    p_resy = -sin_theta * xoff + cos_theta * yoff
    return xc + p_resx, yc + p_resy

def _find_top_left_point(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """找到左上角点并按顺时针重新排序顶点 (私有函数)"""
    points.sort(key=lambda p: (p[1], p[0])) # 按y优先，x次优先排序
    top_left_point = points[0]
    
    # 计算其他点相对于左上角的角度
    def angle_from_top_left(p):
        return math.atan2(p[1] - top_left_point[1], p[0] - top_left_point[0])

    # 除去左上角点，对剩下三点按角度排序
    remaining_points = sorted(points[1:], key=angle_from_top_left)
    
    return [top_left_point] + remaining_points


# --- 格式转换核心函数 ---

def rolabelimg_to_dota_object(robndbox: Dict) -> List[float]:
    """将单个RoLabelImg对象转换为DOTA四点坐标"""
    cx, cy, w, h, angle = [
        robndbox['cx'], robndbox['cy'], robndbox['w'], robndbox['h'], robndbox['angle']
    ]
    
    # 计算未旋转时的四个顶点
    x_min, y_min = cx - w / 2, cy - h / 2
    x_max, y_max = cx + w / 2, cy + h / 2

    points = [
        (x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)
    ]
    
    # 旋转顶点
    rotated_points = [_rotate_point(cx, cy, xp, yp, -angle) for xp, yp in points]
    
    # DOTA格式要求顶点顺时针，且从左上角开始
    # sorted_points = _find_top_left_point(rotated_points)
    
    # 打平列表 [x1, y1, x2, y2, ...]
    flat_points = [coord for point in rotated_points for coord in point]
    return [float(f"{p:.1f}") for p in flat_points]


def dota_to_rolabelimg_object(points: List[float]) -> Dict:
    """将单个DOTA四点坐标转换为RoLabelImg对象"""
    x1, y1, x2, y2, x3, y3, x4, y4 = points
    
    cx = (x1 + x3) / 2
    cy = (y1 + y3) / 2
    
    w = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    h = math.sqrt((x4 - x1)**2 + (y4 - y1)**2)
    
    # 角度计算以第一条边(p1->p2)为准
    angle = math.atan2(y2 - y1, x2 - x1)
    
    return {
        "cx": float(f"{cx:.1f}"),
        "cy": float(f"{cy:.1f}"),
        "w": float(f"{w:.1f}"),
        "h": float(f"{h:.1f}"),
        "angle": float(f"{angle:.4f}")
    }

# --- 文件内容生成函数 ---

def create_rolabelimg_xml(filename: str, img_size: Tuple[int, int], objects: List[Dict]) -> str:
    """生成RoLabelImg格式的XML文件字符串"""
    annotation = ET.Element("annotation")
    ET.SubElement(annotation, "folder").text = "Unknown"
    ET.SubElement(annotation, "filename").text = filename
    
    size_node = ET.SubElement(annotation, "size")
    ET.SubElement(size_node, "width").text = str(img_size[0])
    ET.SubElement(size_node, "height").text = str(img_size[1])
    ET.SubElement(size_node, "depth").text = "3"

    for obj in objects:
        obj_node = ET.SubElement(annotation, "object")
        ET.SubElement(obj_node, "name").text = obj['name']
        ET.SubElement(obj_node, "difficult").text = str(obj['difficult'])
        
        robndbox_node = ET.SubElement(obj_node, "robndbox")
        for key, val in obj['robndbox'].items():
            ET.SubElement(robndbox_node, key).text = str(val)
            
    # 格式化输出
    xml_str = ET.tostring(annotation)
    pretty_xml_str = parseString(xml_str).toprettyxml(indent="    ")
    return pretty_xml_str
