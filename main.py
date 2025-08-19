import os
import argparse
import xml.etree.ElementTree as ET
from tqdm import tqdm
from PIL import Image
from converter import (
    rolabelimg_to_dota_object,
    dota_to_rolabelimg_object,
    create_rolabelimg_xml
)

def convert_rolabelimg_to_dota(xml_dir, txt_dir):
    """处理从 RoLabelImg 到 DOTA 的转换"""
    os.makedirs(txt_dir, exist_ok=True)
    xml_files = [f for f in os.listdir(xml_dir) if f.endswith('.xml')]

    for xml_file in tqdm(xml_files, desc="RoLabelImg -> DOTA"):
        tree = ET.parse(os.path.join(xml_dir, xml_file))
        root = tree.getroot()
        
        dota_objects = []
        for obj in root.findall('object'):
            name = obj.find('name').text
            difficult = obj.find('difficult').text
            robndbox_node = obj.find('robndbox')
            
            robndbox = {child.tag: float(child.text) for child in robndbox_node}
            dota_points = rolabelimg_to_dota_object(robndbox)
            
            dota_line = " ".join(map(str, dota_points)) + f" {name} {difficult}"
            dota_objects.append(dota_line)

        txt_filename = os.path.splitext(xml_file)[0] + '.txt'
        with open(os.path.join(txt_dir, txt_filename), 'w') as f:
            f.write("\n".join(dota_objects))

def convert_dota_to_rolabelimg(txt_dir, img_dir, xml_dir):
    """处理从 DOTA 到 RoLabelImg 的转换"""
    os.makedirs(xml_dir, exist_ok=True)
    txt_files = [f for f in os.listdir(txt_dir) if f.endswith('.txt')]

    for txt_file in tqdm(txt_files, desc="DOTA -> RoLabelImg"):
        base_name = os.path.splitext(txt_file)[0]
        img_path = os.path.join(img_dir, base_name + '.jpg') # 假设图片是.jpg格式
        if not os.path.exists(img_path):
            print(f"Warning: Image file not found for {txt_file}, skipping: {img_path}")
            continue

        img = Image.open(img_path)
        img_size = img.size
        
        xml_objects = []
        with open(os.path.join(txt_dir, txt_file), 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 10: continue
                
                points = list(map(float, parts[:8]))
                name = parts[8]
                difficult = parts[9]
                
                robndbox = dota_to_rolabelimg_object(points)
                xml_objects.append({'name': name, 'difficult': difficult, 'robndbox': robndbox})

        xml_content = create_rolabelimg_xml(os.path.basename(img_path), img_size, xml_objects)
        
        xml_filename = base_name + '.xml'
        with open(os.path.join(xml_dir, xml_filename), 'w') as f:
            f.write(xml_content)


def main():
    parser = argparse.ArgumentParser(description="Annotation format converter for rotated object detection.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-parser for rolabelimg to dota
    parser_ro2dota = subparsers.add_parser("ro2dota", help="Convert RoLabelImg XML to DOTA TXT format.")
    parser_ro2dota.add_argument("--xml-dir", required=True, help="Directory containing RoLabelImg XML files.")
    parser_ro2dota.add_argument("--txt-dir", required=True, help="Directory to save the converted DOTA TXT files.")

    # Sub-parser for dota to rolabelimg
    parser_dota2ro = subparsers.add_parser("dota2ro", help="Convert DOTA TXT to RoLabelImg XML format.")
    parser_dota2ro.add_argument("--txt-dir", required=True, help="Directory containing DOTA TXT files.")
    parser_dota2ro.add_argument("--img-dir", required=True, help="Directory containing the original images.")
    parser_dota2ro.add_argument("--xml-dir", required=True, help="Directory to save the converted RoLabelImg XML files.")

    args = parser.parse_args()

    if args.command == "ro2dota":
        convert_rolabelimg_to_dota(args.xml_dir, args.txt_dir)
    elif args.command == "dota2ro":
        convert_dota_to_rolabelimg(args.txt_dir, args.img_dir, args.xml_dir)
        
    print("Conversion complete!")

if __name__ == "__main__":
    main()
