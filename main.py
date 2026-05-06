from abc import ABC, abstractmethod
from datetime import datetime
import copy


class FileSystemNode(ABC):
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.created_at = datetime.now()
        self.tags = set()

    @abstractmethod
    def get_size(self, log=False):
        pass

    @abstractmethod
    def display(self, prefix="", is_last=True):
        pass

    @abstractmethod
    def to_xml(self, level=0):
        pass

    @abstractmethod
    def search(self, ext, current_path="", log=False):
        pass

    def add_tag(self, tag):
        self.tags.add(tag)

    def tag_label(self):
        if not self.tags:
            return ""
        return " " + " ".join(f"[{t}]" for t in sorted(self.tags))


class Directory(FileSystemNode):
    def __init__(self, name):
        super().__init__(name, 0)
        self.children = []

    def add(self, node):
        self.children.append(node)
        return self

    def remove(self, name):
        for i, child in enumerate(self.children):
            if child.name == name:
                return self.children.pop(i)
        return None

    def find_child(self, name):
        for child in self.children:
            if child.name == name:
                return child
        return None

    def display(self, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{self.name} [目錄]{self.tag_label()}")
        next_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            child.display(next_prefix, i == len(self.children) - 1)

    def get_size(self, log=False):
        if log:
            print(f"  Visiting: {self.name}")
        total = 0
        for child in self.children:
            total += child.get_size(log)
        return total

    def search(self, ext, current_path="", log=False):
        path = f"{current_path}/{self.name}" if current_path else self.name
        if log:
            print(f"  Visiting: {path}")
        results = []
        for child in self.children:
            results.extend(child.search(ext, path, log))
        return results

    def to_xml(self, level=0):
        indent = "    " * level
        tag = self.name.replace(" ", "_")
        inner = "\n".join(child.to_xml(level + 1) for child in self.children)
        return f"{indent}<{tag}>\n{inner}\n{indent}</{tag}>"

    def sort_children(self, by="name", reverse=False):
        if by == "name":
            self.children.sort(key=lambda n: n.name.lower(), reverse=reverse)
        elif by == "size":
            self.children.sort(key=lambda n: n.get_size(), reverse=reverse)
        elif by == "ext":
            self.children.sort(
                key=lambda n: n.name.split(".")[-1].lower() if "." in n.name else "",
                reverse=reverse
            )


class WordFile(FileSystemNode):
    def __init__(self, name, size, page_count):
        super().__init__(name, size)
        self.page_count = page_count

    def get_size(self, log=False):
        if log:
            print(f"  Visiting: {self.name}")
        return self.size

    def display(self, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{self.name} [Word 檔案] (頁數: {self.page_count}, 大小: {self.size}KB){self.tag_label()}")

    def to_xml(self, level=0):
        indent = "    " * level
        tag = self.name.replace(".", "_")
        return f"{indent}<{tag}>頁數: {self.page_count}, 大小: {self.size}KB</{tag}>"

    def search(self, ext, current_path="", log=False):
        full_path = f"{current_path}/{self.name}"
        if log:
            print(f"  Visiting: {full_path}")
        if self.name.lower().endswith(ext.lower()):
            return [full_path]
        return []


class ImageFile(FileSystemNode):
    def __init__(self, name, size, width, height):
        super().__init__(name, size)
        self.width = width
        self.height = height

    def get_size(self, log=False):
        if log:
            print(f"  Visiting: {self.name}")
        return self.size

    def display(self, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{self.name} [圖片] (解析度: {self.width}x{self.height}, 大小: {self.size}KB){self.tag_label()}")

    def to_xml(self, level=0):
        indent = "    " * level
        tag = self.name.replace(".", "_")
        return f"{indent}<{tag}>解析度: {self.width}x{self.height}, 大小: {self.size}KB</{tag}>"

    def search(self, ext, current_path="", log=False):
        full_path = f"{current_path}/{self.name}"
        if log:
            print(f"  Visiting: {full_path}")
        if self.name.lower().endswith(ext.lower()):
            return [full_path]
        return []


class TextFile(FileSystemNode):
    def __init__(self, name, size, encoding):
        super().__init__(name, size)
        self.encoding = encoding

    def get_size(self, log=False):
        if log:
            print(f"  Visiting: {self.name}")
        return self.size

    def display(self, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{self.name} [純文字檔] (編碼: {self.encoding}, 大小: {self.size}KB){self.tag_label()}")

    def to_xml(self, level=0):
        indent = "    " * level
        tag = self.name.replace(".", "_")
        return f"{indent}<{tag}>編碼: {self.encoding}, 大小: {self.size}KB</{tag}>"

    def search(self, ext, current_path="", log=False):
        full_path = f"{current_path}/{self.name}"
        if log:
            print(f"  Visiting: {full_path}")
        if self.name.lower().endswith(ext.lower()):
            return [full_path]
        return []


# Command Pattern: 用來實作 Undo / Redo
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass


class AddCommand(Command):
    def __init__(self, parent, node):
        self.parent = parent
        self.node = node

    def execute(self):
        self.parent.add(self.node)

    def undo(self):
        self.parent.remove(self.node.name)


class RemoveCommand(Command):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.removed = None

    def execute(self):
        self.removed = self.parent.remove(self.name)

    def undo(self):
        if self.removed:
            self.parent.add(self.removed)


class CopyCommand(Command):
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.copied = None

    def execute(self):
        self.copied = copy.deepcopy(self.source)
        self.copied.name = "Copy_of_" + self.source.name
        self.target.add(self.copied)

    def undo(self):
        if self.copied:
            self.target.remove(self.copied.name)


class CommandHistory:
    def __init__(self):
        self.history = []
        self.redo_stack = []

    def execute(self, command):
        command.execute()
        self.history.append(command)
        self.redo_stack.clear()

    def undo(self):
        if not self.history:
            print("沒有可以復原的操作")
            return
        command = self.history.pop()
        command.undo()
        self.redo_stack.append(command)

    def redo(self):
        if not self.redo_stack:
            print("沒有可以重做的操作")
            return
        command = self.redo_stack.pop()
        command.execute()
        self.history.append(command)


def build_sample_data():
    root = Directory("根目錄 (Root)")

    project_docs = Directory("專案文件 (Project_Docs)")
    project_docs.add(WordFile("需求規格書.docx", 500, 15))
    project_docs.add(ImageFile("系統架構圖.png", 2048, 1920, 1080))

    personal_notes = Directory("個人筆記 (Personal_Notes)")
    personal_notes.add(TextFile("待辦清單.txt", 1, "UTF-8"))

    archive = Directory("2025備份 (Archive_2025)")
    archive.add(WordFile("舊會議記錄.docx", 200, 5))
    personal_notes.add(archive)

    root.add(project_docs)
    root.add(personal_notes)
    root.add(TextFile("README.txt", 0.5, "ASCII"))

    return root


def main():
    root = build_sample_data()

    print("\n--- 功能一：目錄結構顯示 ---")
    print(f"{root.name} [目錄]")
    for i, child in enumerate(root.children):
        child.display("", i == len(root.children) - 1)

    print("\n--- 功能二：遞迴計算總容量 ---")
    total = root.get_size(log=True)
    print(f"\n總大小：{total} KB")

    print("\n--- 功能二：搜尋 .docx 檔案 ---")
    results = root.search(".docx", log=True)
    print(f"\n找到 {len(results)} 個檔案：")
    for r in results:
        print(f"  {r}")

    print("\n--- 功能二：XML 輸出 ---")
    print(root.to_xml())

    print("\n--- 加分：排序（依大小降冪）---")
    root.sort_children(by="size", reverse=True)
    print(f"{root.name} [目錄]")
    for i, child in enumerate(root.children):
        child.display("", i == len(root.children) - 1)

    print("\n--- 加分：標籤 ---")
    readme = root.find_child("README.txt")
    readme.add_tag("Urgent")
    readme.add_tag("Work")
    print(f"{root.name} [目錄]")
    for i, child in enumerate(root.children):
        child.display("", i == len(root.children) - 1)

    print("\n--- 加分：Undo / Redo ---")
    history = CommandHistory()
    new_file = TextFile("新備忘錄.txt", 2, "UTF-8")

    history.execute(AddCommand(root, new_file))
    print(f"新增後子節點數：{len(root.children)}")

    history.undo()
    print(f"Undo 後子節點數：{len(root.children)}")

    history.redo()
    print(f"Redo 後子節點數：{len(root.children)}")

    print("\n--- 加分：複製 ---")
    notes = root.find_child("個人筆記 (Personal_Notes)")
    history.execute(CopyCommand(readme, notes))
    notes.display("", True)


if __name__ == "__main__":
    main()
