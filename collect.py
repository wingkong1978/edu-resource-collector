#!/usr/bin/env python3
"""
中学教育资源采集脚本
简化版 - 使用 Markdown 文件组织资源
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent
RESOURCES_DIR = BASE_DIR / "resources"

# 学科映射
SUBJECTS = {
    "语文": ["初中", "高中"],
    "数学": ["初中", "高中"],
    "英语": ["初中", "高中"],
    "物理": ["初中", "高中"],
    "化学": ["初中", "高中"],
    "生物": ["初中", "高中"],
    "历史": ["初中", "高中"],
    "地理": ["初中", "高中"],
    "政治": ["初中", "高中"],
}

RESOURCE_TYPES = ["视频", "文档", "试卷", "课件", "笔记", "软件"]


def get_next_number(subject_dir: Path) -> int:
    """获取下一个序号"""
    if not subject_dir.exists():
        return 1
    
    files = list(subject_dir.glob("*.md"))
    if not files:
        return 1
    
    numbers = []
    for f in files:
        try:
            num = int(f.name.split("-")[0])
            numbers.append(num)
        except (ValueError, IndexError):
            continue
    
    return max(numbers, default=0) + 1


def create_resource_file(grade: str, subject: str, title: str, resource_type: str = "文档",
                        source: str = "", link: str = "", description: str = "", tags: str = ""):
    """创建资源文件"""
    
    subject_dir = RESOURCES_DIR / grade / subject
    subject_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取序号
    number = get_next_number(subject_dir)
    
    # 生成文件名
    safe_title = title.replace("/", "-").replace("\\", "-")
    filename = f"{number:03d}-{safe_title}.md"
    filepath = subject_dir / filename
    
    # 生成内容
    content = f"""# {title}

- **类型**: {resource_type}
- **学科**: {subject}
- **年级**: {grade}
- **来源**: {source or '未知'}
- **链接**: {link or '暂无'}
- **收录时间**: {datetime.now().strftime('%Y-%m-%d')}
- **标签**: {tags or '#待分类'}

## 描述

{description or '暂无描述'}

## 内容摘要

<!-- 在这里添加资源内容的简要说明 -->

## 适用场景

<!-- 描述这个资源适合什么情况下使用 -->

## 备注

<!-- 其他需要记录的信息 -->
"""
    
    # 写入文件
    filepath.write_text(content, encoding='utf-8')
    print(f"✅ 已创建: {filepath}")
    return filepath


def generate_index():
    """生成汇总索引"""
    index_file = BASE_DIR / "汇总.md"
    
    lines = [
        "# 中学教育资源汇总",
        "",
        f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 目录",
        "",
    ]
    
    total_count = 0
    
    for grade in ["初中", "高中"]:
        lines.append(f"## {grade}")
        lines.append("")
        
        grade_dir = RESOURCES_DIR / grade
        if not grade_dir.exists():
            continue
        
        for subject in SUBJECTS.keys():
            subject_dir = grade_dir / subject
            if not subject_dir.exists():
                continue
            
            files = list(subject_dir.glob("*.md"))
            count = len(files)
            total_count += count
            
            if count > 0:
                lines.append(f"### {subject} ({count}个资源)")
                lines.append("")
                
                for f in sorted(files):
                    # 读取标题
                    content = f.read_text(encoding='utf-8')
                    title = content.split('\n')[0].replace('# ', '') if content else f.stem
                    
                    lines.append(f"- [{title}](resources/{grade}/{subject}/{f.name})")
                
                lines.append("")
    
    lines.insert(4, f"**资源总数**: {total_count} 个")
    lines.insert(5, "")
    
    index_file.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✅ 汇总索引已生成: {index_file}")
    print(f"   共收录 {total_count} 个资源")


def list_resources(grade: str = None, subject: str = None):
    """列出资源"""
    grades = [grade] if grade else ["初中", "高中"]
    
    for g in grades:
        grade_dir = RESOURCES_DIR / g
        if not grade_dir.exists():
            continue
        
        print(f"\n📚 {g}:")
        
        subjects_to_list = [subject] if subject else SUBJECTS.keys()
        
        for s in subjects_to_list:
            subject_dir = grade_dir / s
            if not subject_dir.exists():
                continue
            
            files = list(subject_dir.glob("*.md"))
            if files:
                print(f"  📖 {s}: {len(files)} 个资源")


def interactive_add():
    """交互式添加资源"""
    print("=== 添加教育资源 ===\n")
    
    # 选择学段
    print("选择学段:")
    print("  1. 初中")
    print("  2. 高中")
    grade_choice = input("请输入 (1/2): ").strip()
    grade = "初中" if grade_choice == "1" else "高中"
    
    # 选择学科
    print(f"\n选择学科:")
    subjects_list = list(SUBJECTS.keys())
    for i, s in enumerate(subjects_list, 1):
        print(f"  {i}. {s}")
    subject_idx = int(input("请输入序号: ").strip()) - 1
    subject = subjects_list[subject_idx]
    
    # 输入资源信息
    print(f"\n输入资源信息:")
    title = input("  资源标题: ").strip()
    resource_type = input("  资源类型 (视频/文档/试卷/课件/笔记): ").strip() or "文档"
    source = input("  来源网站: ").strip()
    link = input("  资源链接: ").strip()
    description = input("  资源描述: ").strip()
    tags = input("  标签 (用空格分隔): ").strip()
    
    # 创建文件
    create_resource_file(
        grade=grade,
        subject=subject,
        title=title,
        resource_type=resource_type,
        source=source,
        link=link,
        description=description,
        tags=tags
    )
    
    print("\n✅ 资源添加完成!")


def main():
    parser = argparse.ArgumentParser(description='中学教育资源采集工具')
    parser.add_argument('--add', '-a', action='store_true', help='交互式添加资源')
    parser.add_argument('--index', '-i', action='store_true', help='生成汇总索引')
    parser.add_argument('--list', '-l', action='store_true', help='列出资源')
    parser.add_argument('--grade', '-g', help='年级 (初中/高中)')
    parser.add_argument('--subject', '-s', help='学科')
    parser.add_argument('--title', '-t', help='资源标题')
    parser.add_argument('--type', help='资源类型')
    parser.add_argument('--link', help='资源链接')
    parser.add_argument('--source', help='来源网站')
    parser.add_argument('--desc', help='资源描述')
    
    args = parser.parse_args()
    
    if args.add:
        interactive_add()
    elif args.index:
        generate_index()
    elif args.list:
        list_resources(args.grade, args.subject)
    elif args.title:
        # 快速添加模式
        create_resource_file(
            grade=args.grade or "高中",
            subject=args.subject or "数学",
            title=args.title,
            resource_type=args.type or "文档",
            link=args.link or "",
            source=args.source or "",
            description=args.desc or ""
        )
    else:
        parser.print_help()
        print("\n示例:")
        print("  python collect.py --add                    # 交互式添加")
        print("  python collect.py --index                  # 生成汇总")
        print("  python collect.py --list                   # 列出所有资源")
        print("  python collect.py -g 高中 -s 数学 -t '函数专题'")


if __name__ == '__main__':
    main()
