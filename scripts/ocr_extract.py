# -*- coding: utf-8 -*-
"""
星穹铁道截图批量文字提取工具
使用 RapidOCR 本地识别图片中的文字，支持批量处理。

用法：
  python scripts/ocr_extract.py <图片路径或文件夹> [选项]

选项：
  -o, --output DIR    输出目录（默认：与图片同目录下的 ocr_output）
  -f, --format FMT    输出格式：txt（纯文字）或 json（含坐标/置信度），默认 txt
  -r, --recursive     递归处理子文件夹
  --lang LANG         识别语言（默认：ch，中文+英文）

示例：
  python scripts/ocr_extract.py screenshots/
  python scripts/ocr_extract.py screenshot.png -f json
  python scripts/ocr_extract.py screenshots/ -o output/ -r
"""
import sys, os, re, json, argparse
sys.stdout.reconfigure(encoding='utf-8')

try:
    from rapidocr_onnxruntime import RapidOCR
except ImportError:
    print('错误：未安装 RapidOCR，请运行：pip install rapidocr-onnxruntime')
    sys.exit(1)

# 支持的图片格式
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}


def ocr_image(ocr, image_path):
    """对单张图片进行OCR识别"""
    result, elapse = ocr(image_path)
    # elapse 可能是列表（各阶段耗时）或浮点数
    if isinstance(elapse, (list, tuple)):
        elapse_total = sum(float(e) for e in elapse)
    else:
        elapse_total = float(elapse)
    
    if result is None:
        return [], elapse_total
    
    items = []
    for line in result:
        # line = [box, text, confidence]
        box = line[0]  # 四个角点坐标 [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        text = line[1]
        confidence = line[2]
        # 计算中心点坐标
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        center_x = sum(xs) / 4
        center_y = sum(ys) / 4
        items.append({
            'text': text,
            'confidence': round(float(confidence), 4),
            'box': [[int(p[0]), int(p[1])] for p in box],
            'center': [int(center_x), int(center_y)],
            'y': int(center_y),
            'x': int(center_x)
        })
    
    # 按阅读顺序排序（从上到下，从左到右）
    items.sort(key=lambda x: (x['y'] // 20, x['x']))
    return items, elapse_total


def save_txt(items, output_path, image_name):
    """保存为纯文本"""
    lines = [f'# {image_name}', '']
    for item in items:
        lines.append(item['text'])
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def save_json(items, output_path, image_name, elapse):
    """保存为JSON（含坐标和置信度）"""
    data = {
        'image': image_name,
        'elapse_seconds': round(elapse, 2),
        'text_count': len(items),
        'items': items
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def collect_images(input_path, recursive=False):
    """收集所有图片文件"""
    images = []
    if os.path.isfile(input_path):
        ext = os.path.splitext(input_path)[1].lower()
        if ext in IMAGE_EXTS:
            images.append(input_path)
    elif os.path.isdir(input_path):
        if recursive:
            for root, dirs, fs in os.walk(input_path):
                for f in fs:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in IMAGE_EXTS:
                        images.append(os.path.join(root, f))
        else:
            for f in os.listdir(input_path):
                fp = os.path.join(input_path, f)
                if os.path.isfile(fp):
                    ext = os.path.splitext(f)[1].lower()
                    if ext in IMAGE_EXTS:
                        images.append(fp)
    return images


def main():
    parser = argparse.ArgumentParser(description='星穹铁道截图批量文字提取工具')
    parser.add_argument('input', help='图片路径或文件夹路径')
    parser.add_argument('-o', '--output', default=None, help='输出目录（默认：输入目录/ocr_output）')
    parser.add_argument('-f', '--format', choices=['txt', 'json'], default='txt', help='输出格式（默认：txt）')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子文件夹')
    args = parser.parse_args()
    
    input_path = args.input
    if not os.path.exists(input_path):
        print(f'错误：路径不存在 - {input_path}')
        sys.exit(1)
    
    # 确定输出目录
    if args.output:
        output_dir = args.output
    else:
        if os.path.isfile(input_path):
            output_dir = os.path.join(os.path.dirname(input_path), 'ocr_output')
        else:
            output_dir = os.path.join(input_path, 'ocr_output')
    os.makedirs(output_dir, exist_ok=True)
    
    # 收集图片
    images = collect_images(input_path, args.recursive)
    if not images:
        print('未找到图片文件')
        sys.exit(1)
    
    print(f'找到 {len(images)} 张图片')
    print(f'输出目录: {output_dir}')
    print(f'输出格式: {args.format}')
    print('-' * 50)
    
    # 初始化OCR
    print('加载 OCR 模型...')
    ocr = RapidOCR()
    print('模型加载完成')
    print()
    
    # 批量处理
    success = 0
    failed = 0
    total_texts = 0
    
    for i, img_path in enumerate(images):
        img_name = os.path.basename(img_path)
        print(f'[{i+1}/{len(images)}] {img_name}...', end=' ')
        
        try:
            items, elapse = ocr_image(ocr, img_path)
            total_texts += len(items)
            
            # 生成输出文件名
            base_name = os.path.splitext(img_name)[0]
            if args.format == 'txt':
                out_path = os.path.join(output_dir, f'{base_name}.txt')
                save_txt(items, out_path, img_name)
            else:
                out_path = os.path.join(output_dir, f'{base_name}.json')
                save_json(items, out_path, img_name, elapse)
            
            print(f'完成 ({len(items)} 条文字, {elapse:.2f}s)')
            success += 1
        except Exception as e:
            print(f'失败: {e}')
            failed += 1
    
    print()
    print('=' * 50)
    print(f'处理完成: 成功 {success}, 失败 {failed}')
    print(f'共识别 {total_texts} 条文字')
    print(f'输出目录: {output_dir}')


if __name__ == '__main__':
    main()
