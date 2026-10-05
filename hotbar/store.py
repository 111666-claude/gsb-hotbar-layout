"""快捷栏布局：格子、技能唯一性、批量搬运、撤销与存档。

缺陷：同一个技能可以放进多个格子、批量搬运越界时只搬一半、撤销只弹栈不恢复布局、
同一个 req_id 重复生效、统计全扫格子。
"""


class Layout:
    """快捷栏台账。"""

    def __init__(self, slots):
        self.slots = slots
        self.cells = [None] * slots
        self.history = []
        self.seen = {}
        self.used = 0
        self.work = 0

    def place(self, req_id, slot, skill):
        """把一个技能放进格子，返回是否成功。缺陷：不查技能是否已在栏里、不查 req_id。"""
        self.cells[slot] = skill
        return True

    def move(self, req_id, start, count, shift):
        """把 start 起 count 个格子整体平移 shift，返回是否成功。缺陷：越界只搬能搬的那部分。"""
        for offset in range(count):
            source = start + offset
            target = source + shift
            if 0 <= source < self.slots and 0 <= target < self.slots:
                self.cells[target] = self.cells[source]
        return True

    def undo(self, req_id):
        """撤销上一步，返回是否成功。缺陷：只弹栈，不恢复布局。"""
        if not self.history:
            return False
        self.history.pop()
        return True

    def stats(self):
        """返回 (已占格数, 不同技能数)。缺陷：全扫格子。"""
        self.work += self.slots
        skills = set()
        for cell in self.cells:
            if cell is not None:
                skills.add(cell)
        return self.slots - self.cells.count(None), len(skills)

    def dump(self):
        """把布局序列化成文本。缺陷：不写槽位数，往返会丢信息。"""
        lines = []
        for index, cell in enumerate(self.cells):
            if cell is not None:
                lines.append("%d=%s" % (index, cell))
        return "\n".join(lines) + "\n"

    @classmethod
    def load(cls, text, slots):
        """从文本恢复布局。缺陷：不校验格子下标。"""
        layout = cls(slots)
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            index, _, skill = line.partition("=")
            layout.cells[int(index)] = skill
        return layout

    def work_count(self):
        return self.work
