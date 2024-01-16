def post_content_to_markdown(content, merge_title=True):
    text = []
    for row in content.get("content", []):
        line_text = []
        for item in row:
            item_text = ""
            if "text" == item["tag"]:
                item_text = item["text"]
            elif "at" == item["tag"]:
                item_text = f"@{item['user_name']}"
            elif "a" == item["tag"]:
                item_text = f"[{item['text']}]({item['href']})"
            elif "img" == item["tag"]:
                item_text = f"![]({item['image_key']})"
            elif "media" == item["tag"]:
                pass
            elif "emotion" == item["tag"]:
                pass
            for s in item.get("style", []):
                if "bold" == s:
                    item_text = f"**{item_text}**"
                elif "underline" == s:
                    item_text = f"<ins>{item_text}</ins>"
                elif "italic" == s:
                    item_text = f"_{item_text}_"
                elif "lineThrough" == s:
                    item_text = f"~{item_text}~"
            line_text.append(item_text)
        text.append("".join(line_text))
    title = content.get("title", "")
    content_text = "  ".join(text)
    if merge_title and title:
        content_text = f"# {title}  \n{content_text}"

    return content_text, title


if __name__ == "__main__":
    content = {
        "title": "",
        "content": [
            [{"tag": "text", "text": "/edit", "style": []}],
            [{"tag": "text", "text": "测试描述", "style": []}],
            [{"tag": "text", "text": "测试quote", "style": []}],
            [{"tag": "text", "text": "测试字体", "style": ["bold"]}],
            [{"tag": "text", "text": "测试横线", "style": ["lineThrough"]}],
            [{"tag": "a", "href": "http://baidu.com", "text": "测试链接 ", "style": []}],
            [{"tag": "text", "text": "测试图片", "style": []}],
            [
                {
                    "tag": "img",
                    "image_key": "img_v3_0275_f817893e-89c4-429d-a97d-85d0899a84bg",
                    "width": 651,
                    "height": 297,
                }
            ],
        ],
    }

    text, title = post_content_to_markdown(content)

    print("content: ", content)
    print("post_content_to_markdown: ", title, text)
