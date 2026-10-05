"""快捷栏布局：格子、技能唯一性、批量搬运、撤销与存档。

口径：同一个技能只能占一个格子；批量搬运越界或结果冲突时整体拒绝；
place / move 压入撤销栈，undo 后进先出恢复；同一个 req_id 只生效一次；
dump / load 逐格往返一致；stats 走增量计数，不全扫格子。
"""

import json


class Layout:
    """快捷栏台账。"""

    def __init__(self, slots):
        self.slots = slots
        self.cells = [None] * slots
        self.history = []
        self.seen = {}
        self.used = 0
        self.work = 0
        self.skill_counts = {}

    def _set_cell(self, slot, value):
        old = self.cells[slot]
        if old == value:
            return
        if old is not None:
            self.used -= 1
            self.skill_counts[old] -= 1
            if self.skill_counts[old] == 0:
                del self.skill_counts[old]
        if value is not None:
            self.used += 1
            self.skill_counts[value] = self.skill_counts.get(value, 0) + 1
        self.cells[slot] = value

    def place(self, req_id, slot, skill):
        """把一个技能放进格子，返回是否成功。技能已存在或 req_id 重复时拒绝。"""
        if req_id in self.seen:
            return False
        if not 0 <= slot < self.slots:
            return False
        if skill in self.skill_counts:
            return False
        old = self.cells[slot]
        self._set_cell(slot, skill)
        self.history.append([[slot, old]])
        self.seen[req_id] = True
        return True

    def move(self, req_id, start, count, shift):
        """把 start 起 count 个格子整体平移 shift；越界或结果冲突时整体拒绝。"""
        if req_id in self.seen:
            return False
        if count <= 0:
            return False
        target = start + shift
        if start < 0 or start + count > self.slots:
            return False
        if target < 0 or target + count > self.slots:
            return False
        result = self.cells[:]
        for offset in range(count):
            result[start + offset] = None
        for offset in range(count):
            result[target + offset] = self.cells[start + offset]
        skills = set()
        for cell in result:
            if cell is None:
                continue
            if cell in skills:
                return False
            skills.add(cell)
        entry = []
        for offset in range(count):
            entry.append([start + offset, self.cells[start + offset]])
        for offset in range(count):
            if not start <= target + offset < start + count:
                entry.append([target + offset, self.cells[target + offset]])
        for offset in range(count):
            self._set_cell(start + offset, None)
        for offset in range(count):
            self._set_cell(target + offset, result[target + offset])
        self.history.append(entry)
        self.seen[req_id] = True
        return True

    def undo(self, req_id):
        """撤销上一步，恢复布局；栈空或 req_id 重复返回 False。"""
        if req_id in self.seen:
            return False
        if not self.history:
            return False
        entry = self.history.pop()
        for slot, old in entry:
            self._set_cell(slot, old)
        self.seen[req_id] = True
        return True

    def stats(self):
        """返回 (已占格数, 不同技能数)，走增量计数，O(1)。"""
        self.work += 1
        return self.used, len(self.skill_counts)

    def dump(self):
        """序列化布局；首行写槽位数，并持久化幂等表与撤销栈保证往返一致。"""
        lines = ["slots=%d" % self.slots]
        for index, cell in enumerate(self.cells):
            if cell is not None:
                lines.append("%d=%s" % (index, cell))
        for req_id in self.seen:
            lines.append("req=%s" % req_id)
        for entry in self.history:
            lines.append("undo=" + json.dumps(entry))
        return "\n".join(lines) + "\n"

    @classmethod
    def load(cls, text, slots):
        """从文本恢复布局，校验格子下标；文本带 slots 头时以文本为准。"""
        cells = []
        seen = []
        history = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            key, _, value = line.partition("=")
            if key == "slots":
                slots = int(value)
            elif key == "req":
                seen.append(value)
            elif key == "undo":
                history.append(json.loads(value))
            else:
                cells.append((key, value))
        layout = cls(slots)
        for key, value in cells:
            index = int(key)
            if not 0 <= index < layout.slots:
                raise ValueError("格子下标越界: %d" % index)
            layout._set_cell(index, value)
        for req_id in seen:
            layout.seen[req_id] = True
        layout.history = history
        return layout

    def work_count(self):
        return self.work
